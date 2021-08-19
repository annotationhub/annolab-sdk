from typing import Dict, Any
import requests
from urllib import parse
import logging
from requests.models import Response

import annolab
from annolab import endpoints
from annolab.util.cached_property import cached_property

class ApiHelper(object):

  def __init__(
    self,
    api_key = None,
    api_url = 'https://api.annolab.ai',
  ):
    self.api_url = api_url
    self.api_key = api_key or annolab.api_key


  @property
  def __auth_header(self, key: str = None):
    key = key or self.api_key
    return { 'Authorization': f'Api-Key {key}' }


  @cached_property
  def api_key_info(self):
    return self.get_request(endpoints.ApiKey.get_api_key_info()).json()


  '''
    Returns the default group to use for the api key.
    The default group is the group representing the single user.
  '''
  @cached_property
  def default_owner(self):
    default_owner = None
    for group in self.api_key_info['groups']:
      if (group['isSingleUser'] is True):
        default_owner = group

    return default_owner


  def get_request(self, path: str, body: Dict[str, Any] = None, params: dict = None) -> Response:
    resp = requests.get(
      parse.urljoin(self.api_url, path),
      headers=self.__auth_header,
      json=body
    )

    self.__handle_non_2xx_response(resp)

    return resp


  def post_request(self, path: str, body: Dict[str, Any] = None, params: dict = None):
    resp = requests.post(
      parse.urljoin(self.api_url, path),
      headers=self.__auth_header,
      json=body,
      params=params
    )

    self.__handle_non_2xx_response(resp)

    return resp


  def put_request(self, path: str, data: Any = None, headers = None, params: dict = None):
    resp = requests.put(
      parse.urljoin(self.api_url, path),
      headers=headers,
      data=data,
      params=params
    )

    self.__handle_non_2xx_response(resp)

    return resp


  def __handle_non_2xx_response(self, resp: Response):
    if (resp.status_code >= 300):
      try:
        resp_body = resp.json()
      except:
        resp_body = {}

      message = resp_body['message'] if 'message' in resp_body else 'Unknown Error'

      logging.error(f'{resp.request.method} {resp.request.path_url} failed with message: {message}')
      resp.raise_for_status()
