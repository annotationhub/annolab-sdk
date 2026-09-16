from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union
import io

from annolab import endpoints
from annolab.abstract_upload_status import AbstractUploadStatus
from annolab.api_helper import ApiHelper
from annolab.upload_result import UploadResult

if TYPE_CHECKING:
  # Imported for type hints only. annolab.project imports this module, so a
  # runtime import here would be circular.
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
    project: 'Project' = None,
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
  ) -> UploadResult:
    """
      Upload a PDF to this abstract using the project's create_pdf_source flow.

      ocr defaults to True (the same default as Project.create_pdf_source).
      Pass ocr=False to skip OCR and extract the pdf's embedded text instead.

      Returns an UploadResult with:
        .pending_source  dict  The created pending source.
        .execution       Optional[WorkflowExecution]  The started workflow
                         execution, or None when no workflow was started.
        .wait_until_complete()  Waits on .execution (no-op when None).

      The result also unpacks as (pending_source, execution) for backwards
      compatibility.
    """
    if self.project is None:
      raise Exception('This LandAbstract is not connected to a project')

    return self.project.create_pdf_source(
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


  def get_upload_status(self, detail: str = 'summary') -> AbstractUploadStatus:
    """
      Return the consolidated upload / workflow status for this abstract.

      detail is "summary" (default) or "full". Full includes each source's
      id, name, and workflow status.
    """
    if self.__api is None:
      raise Exception('This LandAbstract is not connected to the API')

    return AbstractUploadStatus.get(self.__api, self.id, detail=detail)


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
