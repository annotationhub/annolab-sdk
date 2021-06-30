from typing import Dict

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