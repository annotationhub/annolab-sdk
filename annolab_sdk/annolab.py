import io
from os import path
from typing import Optional, Dict, Union

from annolab_sdk import endpoints
from annolab_sdk.api_helper import ApiHelper
from annolab_sdk.util.cached_property import cached_property

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


  '''
    Returns the default group to use for the api key.
    The default group is the group representing the single user.
  '''
  @property
  def default_group(self):
    return self.api.default_group


  def find_project(self, name: str, group_name: str = None):
    group_name = group_name or self.default_group['groupName']

    res = self.api.get_request(
      endpoints.Project.get_group_project(group_name, name)
    )

    return Project.create_from_response_json(res.json(), self.api)


  def create_project(self, name: str, group_name: str = None):
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


  def create_pdf_source(self, filepath: str, name: str = None, directory: str = None):
    name = name or path.basename(filepath)

    init_res = self.api.post_request(
      endpoints.Source.post_initialize_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.group_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceName': name,
      })

    upload_url = init_res.json()['uploadUrl']

    with open(filepath, 'r+b') as pdf_file:
      self.api.put_request(upload_url, data = pdf_file, headers={'Content-Type': 'application/pdf'})

    create_res = self.api.post_request(
      endpoints.Source.post_create_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.group_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceIdentifier': name,
      })

    return create_res.json()



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