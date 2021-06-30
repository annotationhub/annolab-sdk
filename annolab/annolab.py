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
  def default_group(self):
    """
      Returns the default group to use for the api key.
      The default group is the group representing the single user.
    """
    return self.__api.default_group


  def find_project(self, name: str, group_name: str = None):
    """
      Find a project by name and (optionally) group name.
      If group name is not passed, the user's default group is used.
    """
    group_name = group_name or self.default_group['groupName']

    res = self.__api.get_request(
      endpoints.Project.get_group_project(group_name, name)
    )

    return Project.create_from_response_json(res.json(), self.__api)


  def create_project(self, name: str, group_name: str = None):
    """
      Create a project.
      If group name is not passed, the user's default group is used.
    """
    group_name = group_name or self.default_group['groupName']

    res = self.__api.post_request(
      endpoints.Project.post_create(),
      {
        'name': name,
        'groupName': group_name
      }
    )

    return Project.create_from_response_json(res.json(), self.__api)
