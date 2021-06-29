import io
from os import path
from typing import Any, Dict, List, Union
import requests

from annolab_sdk import endpoints
from annolab_sdk.api_helper import ApiHelper

class AnnoLab:

  def __init__(
    self,
    api_key = None,
    api_url = 'http://localhost:8080',
  ):
    self.api = ApiHelper(api_key=api_key, api_url=api_url)

  @property
  def api_key_info(self):
    return self.api.api_key_info


  @property
  def default_group(self):
    """
      Returns the default group to use for the api key.
      The default group is the group representing the single user.
    """
    return self.api.default_group


  def find_project(self, name: str, group_name: str = None):
    """
      Find a project by name and (optionally) group name.
      If group name is not passed, the user's default group is used.
    """
    group_name = group_name or self.default_group['groupName']

    res = self.api.get_request(
      endpoints.Project.get_group_project(group_name, name)
    )

    return Project.create_from_response_json(res.json(), self.api)


  def create_project(self, name: str, group_name: str = None):
    """
      Create a project.
      If group name is not passed, the user's default group is used.
    """
    group_name = group_name or self.default_group['groupName']

    res = self.api.post_request(
      endpoints.Project.post_create(),
      {
        'name': name,
        'groupName': group_name
      }
    )

    return Project.create_from_response_json(res.json(), self.api)


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
    self.api = api_helper


  @property
  def project_path(self):
    return f'{self.group_name}/{self.name}'


  def find_source(self, name: str, directory: str = None):
    """
      Search for a source within a project by name and (optionally) directory.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    res = self.api.get_request(
      endpoints.Source.get_source_by_path(
        group_name=self.api.default_group['groupName'],
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

    res = self.api.post_request(
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

    init_res = self.api.post_request(
      endpoints.Source.post_initialize_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.group_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceName': name,
      })

    upload_url = init_res.json()['uploadUrl']

    pdf_file = file if is_io_or_bytes else open(file, 'r+b')
    self.api.put_request(upload_url, data = pdf_file, headers={'Content-Type': 'application/pdf'})

    if (not isinstance(file, bytes)):
      pdf_file.close()

    create_res = self.api.post_request(
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

    res = self.api.post_request(
      endpoints.Source.post_annotations(self.group_name, self.name, directory, source_name),
      {
        'annotations': list(map(Annotation.create_api_annotation, annotations)),
        'relations': list(map(AnnotationRelation.create_api_relation, relations)),
        'preventDuplication': dedup
      })

    return res.json()


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return Project(
      resp_json['name'],
      resp_json['id'],
      resp_json['groupName'],
      resp_json['groupId'],
      resp_json['defaultDirectory'],
      api_helper=api_helper)


from enum import Enum

class SourceType(Enum):
  Text = 'text'
  Pdf = 'pdf'


class Source:

  def __init__(
    self,
    id: int,
    name: str,
    type: SourceType,
    text: str,
    url: str,
    api_helper: ApiHelper
  ):
    self.id = id
    self.name = name
    self.type = type
    self.text = text
    self.url = url
    self.api = api_helper


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return Source(resp_json['name'], resp_json['id'], resp_json['groupName'], resp_json['groupId'], api_helper=api_helper)


class Annotation:

  @staticmethod
  def create_api_annotation(dict: Dict):
    """
    Maps an sdk annotation dict to an api annotation dict, for use in calls to the api.

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
    annotation = { 'annoTypeIdentifier': dict['type'] }

    if ('client_id' in dict): annotation['clientId'] = str(dict['client_id'])
    if ('offsets' in dict): annotation['offsets'] = dict['offsets']
    if ('schema' in dict): annotation['schemaIdentifier'] = dict['schema']
    if ('value' in dict): annotation['value'] = dict['value']
    if ('bbox' in dict): annotation['bbox'] = dict['bbox']
    if ('layer' in dict): annotation['layerIdentifier'] = dict['layer']
    if ('page' in dict): annotation['pageNumber'] = dict['page']
    if ('reviewed' in dict): annotation['isReviewed'] = dict['reviewed']

    return annotation



class AnnotationRelation:

  @staticmethod
  def create_api_relation(dict: Dict):
    """
    Maps an sdk relation dict to an api annotation relation dict, for use in calls to the api.

    AnnotationRelation parameters:
      annotations: [Union[str, int], Union[str, int]]
      type:        str
      schema:      str
      value:       str
      reviewed     bool (Optional)
    """
    relation = {
      'predecessorId': str(dict['annotations'][0]),
      'successorId': str(dict['annotations'][1])
    }

    if ('type' in dict): relation['typeIdentifier'] = dict['client_id']
    if ('schema' in dict): relation['schemaIdentifier'] = dict['schema']
    if ('value' in dict): relation['value'] = dict['value']
    if ('reviewed' in dict): relation['isReviewed'] = dict['reviewed']

    return relation