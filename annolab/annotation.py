from typing import Dict

class Annotation:

  @staticmethod
  def create_api_annotation(dict: Dict):
    """
    Maps an sdk annotation dict to an api annotation dict, for use in calls to the api.

    Annotation parameters:
      type:       str  (Required)
      client_id:  str  (Optional, Required if passing relations)
      schema:     str  (Optional)
      value:      str  (Optional)
      offsets:    [int, int] (Optional)
      text_bounds { 'type': 'Polygon', coordinates: List[List[List[int]]] } (Optional)
      bbox:       [int, int, int, int] (Optional, Ignored if text_bounds are passed)
      layer:      str  (Optional)
      page:       int  (Optional)
      reviewed    bool (Optional)
    """
    annotation = { 'annoTypeIdentifier': dict['type'] }

    if ('client_id' in dict): annotation['clientId'] = str(dict['client_id'])
    if ('offsets' in dict): annotation['offsets'] = dict['offsets']
    if ('schema' in dict): annotation['schemaIdentifier'] = dict['schema']
    if ('value' in dict): annotation['value'] = dict['value']
    if ('bbox' in dict): annotation['bbox'] = dict['bbox']
    if ('text_bounds' in dict): annotation['textBounds'] = dict['text_bounds']
    if ('image_bounds' in dict): annotation['imageBounds'] = dict['image_bounds']
    if ('layer' in dict): annotation['layerIdentifier'] = dict['layer']
    if ('page' in dict): annotation['pageNumber'] = dict['page']
    if ('endPage' in dict): annotation['endPageNumber'] = dict['endPage']
    if ('reviewed' in dict): annotation['isReviewed'] = dict['reviewed']
    if ('source' in dict): annotation['sourceIdentifier'] = dict['source']
    if ('directory' in dict): annotation['directoryIdentifier'] = dict['directory']
    if ('project' in dict): annotation['projectIdentifier'] = dict['project']

    return annotation