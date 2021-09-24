from annolab.project_import import ProjectImport
import os

from annolab import endpoints
from annolab.project import Project
from annolab.api_helper import ApiHelper

class AnnoLab:

  def __init__(
    self,
    api_key = None,
    api_url = 'https://api.annolab.ai',
  ):
    self.__api = ApiHelper(api_key=api_key, api_url=api_url)

  @property
  def api_key_info(self):
    return self.__api.api_key_info


  @property
  def default_owner(self):
    """
      Returns the default group to use for the api key.
      The default group is the group representing the single user.
    """
    return self.__api.default_owner


  def find_project(self, name: str, owner_name: str = None):
    """
      Find a project by name and (optionally) group name.
      If group name is not passed, the user's default group is used.
    """
    owner_name = owner_name or self.default_owner['groupName']

    res = self.__api.get_request(
      endpoints.Project.get_group_project(owner_name, name)
    )

    return Project.create_from_response_json(res.json(), self.__api)


  def create_project(self, name: str, owner_name: str = None, is_public = False):
    """
      Create a project.
      If group name is not passed, the user's default group is used.
    """
    owner_name = owner_name or self.default_owner['groupName']

    res = self.__api.post_request(
      endpoints.Project.post_create(),
      {
        'name': name,
        'groupName': owner_name,
        'isPublic': is_public
      }
    )

    return Project.create_from_response_json(res.json(), self.__api)


  def create_project_from_export(self, filepath: str, name: str = None, owner_name: str = None, is_public=False):
    if (name is None):
      name = os.path.basename(filepath).split('.')[0]

    project = self.create_project(name, owner_name, is_public=is_public)
    project_import = ProjectImport(filepath, project, owner_name)

    project_import.unzip_export()
    project_import.import_all()
    project_import.cleanup()

    return project

