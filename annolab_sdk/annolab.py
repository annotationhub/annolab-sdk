from typing import Optional, Dict

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
    id: Optional[int],
    group_name: str,
    group_id: int,
    api_helper: ApiHelper
  ):
    self.name = name
    self.id = id
    self.group_name = group_name
    self.group_id = group_id
    self.api = api_helper


  @property
  def project_path(self):
    return f'{self.group_name}/{self.name}'


  def find_source(self, name: str, directory: str):
    res = self.api.get_request(
      endpoints.Source.get_source_by_path(
        group_name=self.api.default_group['groupName'],
        project_name=self.name,
        directory_name=directory,
        source_ref_name=name
      )
    )

    return res.json()


  def create_text_source(self, name: str, text: str, directory: str = None):
    body = {
      'projectIdentifier': self.id or self.name,
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


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return Project(resp_json['name'], resp_json['id'], resp_json['groupName'], resp_json['groupId'], api_helper=api_helper)

