from typing import Any, Dict, List, Optional

from polling2 import poll

from annolab import endpoints
from annolab.api_helper import ApiHelper


class AbstractUploadSource:
  """
  A single document in a full abstract upload status payload.
  """

  def __init__(
    self,
    source_id: int,
    name: str,
    status: str,
  ):
    self.source_id = source_id
    self.name = name
    self.status = status


  @staticmethod
  def create_from_response_json(resp_json: Dict):
    return AbstractUploadSource(
      source_id=resp_json.get('sourceId'),
      name=resp_json.get('name'),
      status=resp_json.get('status'),
    )


  def __repr__(self):
    return (
      f'AbstractUploadSource(source_id={self.source_id!r}, '
      f'name={self.name!r}, status={self.status!r})'
    )


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
    sources: Optional[List[AbstractUploadSource]] = None,
    is_terminal: bool = False,
    detail: str = 'summary',
    api_helper: ApiHelper = None,
  ):
    self.abstract_id = abstract_id
    self.status = status
    self.is_terminal = is_terminal
    self.counts = counts or {
      'sources': 0,
      'ready': 0,
      'running': 0,
      'failed': 0,
    }
    self.blockers = blockers or {}
    self.sources = sources
    self.detail = detail
    self.__api = api_helper


  @property
  def ready_count(self) -> int:
    return self.counts.get('ready', 0)


  @property
  def running_count(self) -> int:
    return self.counts.get('running', 0)


  @property
  def failed_count(self) -> int:
    return self.counts.get('failed', 0)


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper, detail: str = 'summary'):
    sources = None
    if 'sources' in resp_json:
      sources = [
        AbstractUploadSource.create_from_response_json(source)
        for source in (resp_json.get('sources') or [])
      ]

    return AbstractUploadStatus(
      abstract_id=resp_json['abstractId'],
      status=resp_json.get('status'),
      is_terminal=bool(resp_json.get('isTerminal')),
      counts=resp_json.get('counts') or {},
      blockers=_parse_blockers(resp_json.get('blockers') or {}),
      sources=sources,
      detail=detail,
      api_helper=api_helper,
    )


  @staticmethod
  def get(api_helper: ApiHelper, abstract_id: int, detail: str = 'summary'):
    res = api_helper.get_request(
      endpoints.Abstract.get_runsheet_status(abstract_id),
      params={'detail': detail},
    )
    return AbstractUploadStatus.create_from_response_json(res.json(), api_helper, detail)


  def refresh_status(self):
    """
      Query the abstract runsheet status endpoint and refresh this object's
      status, counts, blockers, and sources.
    """
    if self.__api is None:
      raise Exception('This AbstractUploadStatus is not connected to the API')

    res = self.__api.get_request(
      endpoints.Abstract.get_runsheet_status(self.abstract_id),
      params={'detail': self.detail},
    )
    refreshed = AbstractUploadStatus.create_from_response_json(
      res.json(),
      self.__api,
      self.detail,
    )

    self.status = refreshed.status
    self.is_terminal = refreshed.is_terminal
    self.counts = refreshed.counts
    self.blockers = refreshed.blockers
    self.sources = refreshed.sources

    return self.status


  def wait_until_complete(self, timeout: float = 3600, poll_rate: float = None):
    """
      Poll the abstract upload status until is_terminal is true: no workflows
      are running and every workflow has reached a terminal state.

      poll_rate is the number of seconds between status checks. It defaults
      to 15 seconds and cannot be less than 5 seconds.
    """
    step = max(self.min_poll_rate, poll_rate if poll_rate is not None else self.default_poll_rate)

    self.refresh_status()

    if not self.is_terminal:
      poll(
        self._reached_terminal,
        step=step,
        timeout=timeout
      )

    return self


  def _reached_terminal(self):
    self.refresh_status()
    return self.is_terminal


  def __repr__(self):
    return (
      f'AbstractUploadStatus(abstract_id={self.abstract_id!r}, status={self.status!r}, '
      f'is_terminal={self.is_terminal!r}, counts={self.counts!r}, '
      f'blockers={self.blockers!r}, sources={self.sources!r})'
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
