from typing import Any, Dict, List, Optional

from annolab.api_helper import ApiHelper


class LandAbstract:
  """
  A land abstract created or loaded through the API.
  """

  def __init__(
    self,
    id: int,
    name: str,
    key: str,
    project_id: int,
    tags: List[Any],
    instruments: List[Any],
    created_at: str,
    updated_at: str,
    created_by: Optional[Dict[str, Any]],
    updated_by: Optional[Dict[str, Any]],
    api_helper: ApiHelper = None,
    project: Any = None,
  ):
    self.id = id
    self.name = name
    self.key = key
    self.project_id = project_id
    self.tags = tags or []
    self.instruments = instruments or []
    self.created_at = created_at
    self.updated_at = updated_at
    self.created_by = created_by
    self.updated_by = updated_by
    self.project = project
    self.__api = api_helper


  @staticmethod
  def create_from_response_json(
    resp_json: Dict,
    api_helper: ApiHelper,
    project: Any = None,
    name: str = None,
  ):
    return LandAbstract(
      id=resp_json['id'],
      name=name or resp_json.get('name'),
      key=resp_json.get('key'),
      project_id=resp_json.get('projectId'),
      tags=resp_json.get('tags') or [],
      instruments=resp_json.get('instruments') or [],
      created_at=resp_json.get('createdAt'),
      updated_at=resp_json.get('updatedAt'),
      created_by=resp_json.get('createdBy'),
      updated_by=resp_json.get('updatedBy'),
      api_helper=api_helper,
      project=project,
    )
