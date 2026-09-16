from typing import Any, Dict, Optional

from polling2 import poll

from annolab import endpoints
from annolab.api_helper import ApiHelper


TERMINAL_UPLOAD_STATUSES = {
  'READY',
  'ERRORED',
}


class AbstractUploadStatus:
  """
  Consolidated upload / workflow status for an abstract, returned by
  GET /v1/abstract/runsheet-status/:abstractId.
  """

  min_poll_rate = 5
  default_poll_rate = 15

  def __init__(
    self,
    abstract_id: int,
    status: str,
    counts: Optional[Dict[str, int]] = None,
    blockers: Optional[Dict[Any, Dict[str, Any]]] = None,
    api_helper: ApiHelper = None,
  ):
    self.abstract_id = abstract_id
    self.status = status
    self.counts = counts or {
      'sources': 0,
      'ready': 0,
      'running': 0,
      'failed': 0,
    }
    self.blockers = blockers or {}
    self.__api = api_helper


  @property
  def sources(self) -> int:
    return self.counts.get('sources', 0)


  @property
  def ready(self) -> int:
    return self.counts.get('ready', 0)


  @property
  def running(self) -> int:
    return self.counts.get('running', 0)


  @property
  def failed(self) -> int:
    return self.counts.get('failed', 0)


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return AbstractUploadStatus(
      abstract_id=resp_json['abstractId'],
      status=resp_json.get('status'),
      counts=resp_json.get('counts') or {},
      blockers=_parse_blockers(resp_json.get('blockers') or {}),
      api_helper=api_helper,
    )


  @staticmethod
  def get(api_helper: ApiHelper, abstract_id: int):
    res = api_helper.get_request(endpoints.Abstract.get_runsheet_status(abstract_id))
    return AbstractUploadStatus.create_from_response_json(res.json(), api_helper)


  def refresh_status(self):
    """
      Query the abstract runsheet status endpoint and refresh this object's
      status, counts, and blockers.
    """
    if self.__api is None:
      raise Exception('This AbstractUploadStatus is not connected to the API')

    res = self.__api.get_request(endpoints.Abstract.get_runsheet_status(self.abstract_id))
    refreshed = AbstractUploadStatus.create_from_response_json(res.json(), self.__api)

    self.status = refreshed.status
    self.counts = refreshed.counts
    self.blockers = refreshed.blockers

    return self.status


  def wait_until_complete(self, timeout: float = 3600, poll_rate: float = None):
    """
      Poll the abstract upload status until it reaches a terminal status:
      READY or ERRORED.

      poll_rate is the number of seconds between status checks. It defaults
      to 15 seconds and cannot be less than 5 seconds.
    """
    step = max(self.min_poll_rate, poll_rate if poll_rate is not None else self.default_poll_rate)

    self.refresh_status()

    if self.status not in TERMINAL_UPLOAD_STATUSES:
      poll(
        lambda: self.refresh_status() in TERMINAL_UPLOAD_STATUSES,
        step=step,
        timeout=timeout
      )

    return self


  def __repr__(self):
    return (
      f'AbstractUploadStatus(abstract_id={self.abstract_id!r}, status={self.status!r}, '
      f'counts={self.counts!r}, blockers={self.blockers!r})'
    )


def _parse_blockers(blockers: Dict) -> Dict[Any, Dict[str, Any]]:
  parsed = {}
  for key, value in blockers.items():
    try:
      source_id = int(key)
    except (TypeError, ValueError):
      source_id = key
    parsed[source_id] = value
  return parsed
