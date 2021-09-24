import json
from logging import Logger
import requests
import shutil

from annolab.api_helper import ApiHelper
from annolab import endpoints
from polling2 import poll

from enum import Enum

logger = Logger(__name__)

class ExportStatus(Enum):
  initialized = 'initalized'
  started     = 'started'
  errored     = 'errored'
  finished    = 'finished'

class ProjectExport:

  # How often to poll for export status, in seconds.
  poll_rate = 5

  def __init__(
    self,
    api_helper: ApiHelper,
    project,
    options: dict
  ):
    self.__api = api_helper
    self.project = project
    self.options = options
    self.status_url = None
    self.last_status = None
    self.download_url = None
    self.error = None


  def download_on_finish(self, filepath: str, timeout=3600):
    if (self.status_url is None):
      self.start()

    def check_completion():
      self.refresh_status()
      return self.last_status in [ExportStatus.finished.value, ExportStatus.errored.value]

    poll(
      lambda: check_completion(),
      step=self.poll_rate,
      timeout=timeout
    )

    with requests.get(self.download_url, stream=True) as r:
      with open(filepath, 'wb') as f:
        shutil.copyfileobj(r.raw, f)


  def start(self):
    body = {
      'projectIdentifier': self.project.name,
      'groupName' : self.project.owner_name,
      'includeSchemas': self.options.get('include_schemas', False),
      'includeSources': self.options.get('include_sources', False),
      'includeTextBounds': self.options.get('include_text_bounds', False)
    }

    if (self.options.get('source_ids', None) is not None):
      body['sourceIds'] = self.options.source_ids
    if (self.options.get('layers', None) is not None):
      body['annotationLayerNames'] = self.options.layers

    res = self.__api.post_request(
      endpoints.Export.post_export_project(),
      body
    )

    self.status_url = res.json().get('exportStatusUrl', None)

    if (self.status_url is None):
      raise Exception(f'Export status url not returned with response: {json.dumps(res)}')


  def refresh_status(self):
    if (self.status_url is None):
      raise Exception(f'Unable to request export status. No status url. Did you start the export using export.start()?')

    res = self.__api.get_request(self.status_url)

    body = res.json()
    self.last_status = body.get('status', self.last_status)

    if (self.last_status == ExportStatus.finished.value):
      self.download_url = body.get('downloadUrl')

    if (self.last_status == ExportStatus.errored.value):
      self.error = body.get('error')

    return self.last_status

