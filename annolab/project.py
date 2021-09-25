import io
from os import path
from typing import Any, Dict, List, Union
import requests

from annolab import endpoints
from annolab.api_helper import ApiHelper
from annolab.annotation import Annotation
from annolab.annotation_relation import AnnotationRelation
from annolab.project_import import ProjectImport
from annolab.project_export import ProjectExport

class Project:

  def __init__(
    self,
    name: str,
    id: int,
    owner_name: str,
    owner_id: int,
    default_dir: str,
    api_helper: ApiHelper
  ):
    self.name = name
    self.id = id
    self.owner_name = owner_name
    self.owner_id = owner_id
    self.default_dir = default_dir
    self.__api = api_helper


  @property
  def project_path(self):
    return f'{self.owner_name}/{self.name}'


  def find_source(self, name: str, directory: str = None):
    """
      Search for a source within a project by name and (optionally) directory.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    res = self.__api.get_request(
      endpoints.Source.get_source_by_path(
        owner_name=self.__api.default_owner['groupName'],
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
      'groupName': self.owner_name,
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


  def create_pdf_source(
    self, 
    file: Union[str, io.IOBase, bytes], 
    name: str = None, 
    directory: str = None, 
    ocr: bool = False,
    preprocessor: str = 'none',
    **params: dict):
    """
      Creates a pdf source from a local file, bytes, or filelike object.
      If directory is not provided, the default directory is used (typically "Uploads").
      Will OCR using your account preferred OCR if ocr parameter is set to True (Org only)
    """
    is_io_or_bytes = isinstance(file, io.IOBase) or isinstance(file, bytes)
    if (is_io_or_bytes and name is None):
      raise Exception('You must provide a name when passing a filelike object for pdf source creation')

    name = name or path.basename(file)

    init_res = self.__api.post_request(
      endpoints.Source.post_initialize_pdf(),
      {
        'projectIdentifier': self.id or self.name,
        'groupName': self.owner_name,
        'directoryIdentifier': directory or self.default_dir,
        'sourceName': name,
      })

    upload_url = init_res.json()['uploadUrl']

    pdf_file = file if is_io_or_bytes else open(file, 'r+b')
    self.__api.put_request(upload_url, data = pdf_file, headers={'Content-Type': 'application/pdf'})

    if (not isinstance(file, bytes)):
      pdf_file.close()

    body = {
      'projectIdentifier': self.id or self.name,
      'groupName': self.owner_name,
      'directoryIdentifier': directory or self.default_dir,
      'sourceIdentifier': name,
      'ocr': ocr,
      'preprocessor': preprocessor
    }

    body.update(params)

    create_res = self.__api.post_request(
      endpoints.Source.post_create_pdf(),
      body)

    return create_res.json()


  def create_pdf_source_from_web(self, url: str, name: str = None, directory: str = None, **params: dict):
    """
      Creates a pdf source from a web url.
      If directory is not provided, the default directory is used (typically "Uploads").
    """
    name = name or path.basename(url)
    res = requests.get(url)

    if (res.status_code >= 300):
      res.raise_for_status()

    return self.create_pdf_source(res.content, name, directory, params)


  def create_annotations(
    self,
    source_name: str,
    annotations: List[Any],
    relations: List[Any] = [],
    dedup: bool = True,
    directory: str = None):
    """
      Create annotations against a single source.

      Annotation parameters:
        type:       str  (Required)
        client_id:  str  (Optional, Required if passing relations)
        schema:     str  (Optional)
        value:      str  (Optional)
        offsets:    [int, int] (Optional)
        text_bounds dict { 'type': 'Polygon' or 'MultiPolygon', coordinates: List[][][] } (Optional)
        image_bounds dict { 'type': 'Polygon' or 'MultiPolygon', coordinates: List[][][] } (Optional)
        bbox:       [int, int, int, int] (Optional)
        layer:      str  (Optional)
        page:       int  (Optional) Required for classification annotations.
        end_page    int  (Optional) Required for classification annotations.
        reviewed    bool (Optional)
    """
    directory = directory or self.default_dir

    res = self.__api.post_request(
      endpoints.Source.post_annotations(self.owner_name, self.name, directory, source_name),
      {
        'annotations': list(map(Annotation.create_api_annotation, annotations)),
        'relations': list(map(AnnotationRelation.create_api_relation, relations)),
        'preventDuplication': dedup
      })

    return res.json()


  def create_bulk_annotations(
    self,
    annotations: List[Any],
    dedup = True,
  ):
    """
      Create bulk annotations against one or more sources.
      To use this insert method, the annotation must include the project name or id.

      Annotation parameters:
        source     str or int (Required)
        project    str or int (Required)
        type:      str  (Required)
        client_id: str  (Optional, Required if passing relations)
        schema:    str  (Optional)
        value:     str  (Optional)
        offsets:   [int, int] (Optional)
        text_bounds dict { 'type': 'Polygon' or 'MultiPolygon', coordinates: List[][][] } (Optional)
        image_bounds dict { 'type': 'Polygon' or 'MultiPolygon', coordinates: List[][][] } (Optional)
        bbox:      [int, int, int, int] (Optional)
        layer:     str  (Optional)
        page:      int  (Optional) Required for classification annotations.
        end_page   int  (Optional) Required for classification annotations.
        reviewed   bool (Optional)
    """
    res = self.__api.post_request(
      endpoints.Annotation.post_bulk_create(),
      {
        'annotations': list(map(Annotation.create_api_annotation, annotations)),
        'preventDuplication': dedup
      }
    )

    return res.json()


  def create_bulk_relations(
    self,
    relations: List[Any],
    dedup = True
  ):
    """
    Create bulk relations against one or more sources.
    To use this insert method, the annotation must include the project name or id.

    AnnotationRelation parameters:
      annotations:      [Union[str, int], Union[str, int]]
      type:             str  (Required)
      schema:           str  (Required)
      value:            str  (Optional)
      reviewed          bool (Optional)
      project           Union[str, int]
    """
    res = self.__api.post_request(
      endpoints.AnnotationRelation.post_bulk_create(),
      {
        'relations': list(map(AnnotationRelation.create_api_relation, relations)),
        'preventDuplication': dedup
      }
    )

    return res.json()


  def create_annotation_schema(self, name: str):
    """
      Create an annotation schema.

      Annotation schema parameters:
        name:       str  (Required)
    """
    res = self.__api.post_request(
      endpoints.AnnotationSchema.post_create(),
      {
        'schemaName': name,
        'projectIdentifier': self.id
      }
    )

    return res.json()


  def create_annotation_type(self, name: str, **kargs):
    """
      Create an annotation type.

      Annotation type parameters:
        schema:      str or int (Required)
        name:        str  (Required)
        color:       str  (Optional)
        is_relation: str  (Optional, Defaults to false)
        is_document_classification: str  (Optional, Defaults to false)
    """
    res = self.__api.post_request(
      endpoints.AnnotationType.post_create(),
      {
        'schemaIdentifier': kargs.get('schema'),
        'projectIdentifier': self.id,
        'typeName': name,
        'color': kargs.get('color', None),
        'isRelation': kargs.get('is_relation', False),
        'isDocumentClassification': kargs.get('is_document_classification', False),
      }
    )

    return res.json()


  def create_annotation_layer(self, name: str, is_gold: bool = False, description: str = None):
    """
      Create an annotation layer.

      Annotation type parameters:
        name:        str  (Required)
        is_gold:     bool (Optional, Defaults to False)
        description: str  (Optional)
    """
    res = self.__api.post_request(
      endpoints.AnnotationLayer.post_create(),
      {
        'projectIdentifier': self.id,
        'layerName': name,
        'isGold': is_gold,
        'description': description,
      }
    )

    return res.json()


  def export(
    self,
    filepath: str,
    source_ids: List[int] = None,
    layers: List[str] = None,
    include_schemas: bool = False,
    include_sources: bool = False,
    include_text_bounds: bool = False,
    timeout: int = 3600
  ):
    body = {
      'projectIdentifier': self.name,
      'groupName' : self.owner_name,
      'includeSchemas': include_schemas,
      'includeSources': include_sources,
      'includeTextBounds': include_text_bounds
    }

    if (source_ids is not None): body['sourceIds'] = source_ids
    if (layers is not None): body['annotationLayerNames'] = layers

    export = ProjectExport(
      self.__api,
      self,
      {
        'source_ids': source_ids,
        'layers': layers,
        'include_schemas': include_schemas,
        'include_sources': include_sources,
        'include_text_bounds': include_text_bounds
      })

    export.start()
    export.download_on_finish(filepath, timeout=timeout)


  def update_from_export(self, filepath: str, skip_sources=False):
    project_import = ProjectImport(filepath, self, self.owner_name)

    project_import.unzip_export()

    if (skip_sources):
      project_import.import_schemas()
      project_import.import_layers()
      project_import.create_source_map()
      project_import.import_annotations()
      project_import.import_relations()
    else:
      project_import.import_all()

    project_import.cleanup()


  @staticmethod
  def create_from_response_json(resp_json: Dict, api_helper: ApiHelper):
    return Project(
      resp_json['name'],
      resp_json['id'],
      resp_json['groupName'],
      resp_json['groupId'],
      resp_json['defaultDirectory'],
      api_helper=api_helper,)
