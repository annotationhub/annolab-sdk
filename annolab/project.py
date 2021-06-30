import io
from os import path
from typing import Any, Dict, List, Union
import requests

from annolab import endpoints
from annolab.api_helper import ApiHelper
from annolab.annotation import Annotation
from annolab.annotation_relation import AnnotationRelation

class Project:

  def __init__(
    self,
    name: str,
    id: int,
    group_name: str,
    group_id: int,
    default_dir: str,
    api_helper: ApiHelper
  ):
    self.name = name
    self.id = id
    self.group_name = group_name
    self.group_id = group_id
    self.default_dir = default_dir
    self.__api = api_helper


  @property
  def project_path(self):
    return f'{self.group_name}/{self.name}'


  def find_source(self, name: str, directory: str = None):
    """
      Search for a source within a project by name and (optionally) directory.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    res = self.__api.get_request(
      endpoints.Source.get_source_by_path(
        group_name=self.__api.default_group['groupName'],
        project_name=self.name,
        directory_name=directory or self.default_dir,
        source_ref_name=name
      )
    )

    return res.json()


  def create_text_source(self, name: str, text: str, directory: str = None):
    """
      Creates a text source.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    body = {
      'projectIdentifier': self.id or self.name,
      'groupName': self.group_name,
      'sourceName': name,
      'text': text
    }

    if (directory is not None):
      body['directoryIdentifier'] = directory

    res = self.__api.post_request(
      endpoints.Source.post_create_text(),
      body
    )

    return res.json()


  def create_pdf_source(self, file: Union[str, io.IOBase, bytes], name: str = None, directory: str = None):
    """
      Creates a pdf source from a local file, bytes, or filelike object.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    is_io_or_bytes = isinstance(file, io.IOBase) or isinstance(file, bytes)
    if (is_io_or_bytes and name is None):
      raise Exception('You must provide a name when passing a filelike object for pdf source creation')

    name = name or path.basename(file)

    init_res = self.__api.post_request(
      endpoints.Source.post_initialize_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.group_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceName': name,
      })

    upload_url = init_res.json()['uploadUrl']

    pdf_file = file if is_io_or_bytes else open(file, 'r+b')
    self.__api.put_request(upload_url, data = pdf_file, headers={'Content-Type': 'application/pdf'})

    if (not isinstance(file, bytes)):
      pdf_file.close()

    create_res = self.__api.post_request(
      endpoints.Source.post_create_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.group_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceIdentifier': name,
      })

    return create_res.json()


  def create_pdf_source_from_web(self, url: str, name: str = None, directory: str = None):
    """
      Creates a pdf source from a web url.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    name = name or path.basename(url)
    res = requests.get(url)

    if (res.status_code >= 300):
      res.raise_for_status()

    return self.create_pdf_source(res.content, name, directory)


  def create_annotations(
    self,
    source_name: str,
    annotations: List[Any],
    relations: List[Any] = [],
    dedup: bool = True,
    directory: str = None):
    """
      Create annotations against a source.

      Annotation parameters:
        type:      str  (Required)
        client_id: str  (Optional, Required if passing relations)
        schema:    str  (Optional)
        value:     str  (Optional)
        offsets:   [int, int] (Optional)
        bbox:      [int, int, int, int] (Optional)
        layer:     str  (Optional)
        page:      int  (Optional)
        reviewed   bool (Optional)
    """
    directory = directory or self.default_dir

    res = self.__api.post_request(
      endpoints.Source.post_annotations(self.group_name, self.name, directory, source_name),
      {
        'annotations': list(map(Annotation.create_api_annotation, annotations)),
        'relations': list(map(AnnotationRelation.create_api_relation, relations)),
        'preventDuplication': dedup
      })

    return res.json()


  def export(
    self,
    filepath: str,
    source_ids: List[int] = None,
    layers: List[str] = None,
    include_schemas: bool = False,
    include_sources: bool = False
  ):
    body = {
      'projectIdentifier': self.name,
      'groupName' : self.group_name,
      'includeSchemas': include_schemas,
      'includeSources': include_sources
    }

    if (source_ids is not None): body['sourceIds'] = source_ids
    if (layers is not None): body['annotationLayerNames'] = layers

    res = self.__api.post_request(
      endpoints.Export.post_export_project(),
      body
    )

    with open(filepath, 'wb') as f:
      f.write(res.content)


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return Project(
      resp_json['name'],
      resp_json['id'],
      resp_json['groupName'],
      resp_json['groupId'],
      resp_json['defaultDirectory'],
      api_helper=api_helper)
