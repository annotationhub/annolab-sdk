from typing import Any, Dict, List, Optional, Union
import io

from annolab import endpoints
from annolab.api_helper import ApiHelper
from annolab.workflow_execution import WorkflowExecution
from annolab.project import Project


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
    project: Project = None,
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


  def populate_instruments(self, timeout: float = 120.0):
    """
      Page through the land instrument search API and store every instrument
      on this abstract.
    """
    if self.__api is None:
      raise Exception('This LandAbstract is not connected to the API')

    body = {
      'projectIdentifier': self.project.id if self.project is not None else self.project_id,
      'abstractIdentifier': self.id,
    }

    if self.project is not None:
      body['groupName'] = self.project.owner_name

    instruments = []
    page = 1

    while True:
      body['page'] = page
      res = self.__api.post_request(
        endpoints.Abstract.post_search_land_instruments(),
        body,
        timeout=timeout
      )
      data = res.json()
      instruments.extend(data.get('results') or [])

      if not data.get('hasMorePages'):
        break

      page = (data.get('page') or page) + 1

    self.instruments = instruments
    return self


  def upload_file(
    self,
    file: Union[str, io.IOBase, bytes],
    name: str = None,
    directory: str = None,
    ocr: bool = True,
    preprocessor: str = 'none',
    timeout: float = 30.0,
    metadata: dict = None,
    workflow: str = None,
    **params: dict
  ):
    """
      Upload a PDF to this abstract using the project's create_pdf_source flow.

      Returns (pending_source, workflow_execution). workflow_execution is None
      when the upload did not start a workflow.
    """
    if self.project is None:
      raise Exception('This LandAbstract is not connected to a project')

    create_json = self.project.create_pdf_source(
      file=file,
      name=name,
      directory=directory,
      ocr=ocr,
      preprocessor=preprocessor,
      timeout=timeout,
      metadata=metadata,
      abstractId=self.id,
      workflow=workflow,
      **params
    )

    pending_source = create_json.get('pendingSource')
    execution = None
    execution_id = create_json.get('executionId')

    if execution_id:
      execution = WorkflowExecution.get(self.__api, execution_id)

    return pending_source, execution


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
