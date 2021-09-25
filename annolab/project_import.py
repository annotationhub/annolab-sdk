from http import HTTPStatus
from logging import Logger
import os
import re
import shutil
import tempfile
from uuid import uuid4
from typing import Union, List

import jsonlines
from requests.exceptions import HTTPError

logger = Logger(__name__)

class ProjectImport:

  source_file: str = None
  bounds_file: str = None
  annotations_file: str = None
  layers_file: str = None
  relations_file: str = None
  schemas_file: str = None
  atntypes_file: str = None

  # Maps original source id to source name + directory
  source_map: dict = {}
  annotation_map: dict = {}

  def __init__(
    self,
    export_filepath: str,
    project,
    groupId: Union[str, int]
  ):
    self.export_filepath = export_filepath
    self.project = project
    self.groupId = groupId
    self.unpack_target_dir = os.path.join(tempfile.gettempdir(), str(uuid4()))


  def unzip_export(self):
    if not os.path.exists(self.unpack_target_dir):
      os.mkdir(self.unpack_target_dir)

    shutil.unpack_archive(self.export_filepath, self.unpack_target_dir)
    self.__find_entity_files()


  def import_all(self):
    self.import_sources()
    self.import_schemas()
    self.import_layers()
    self.import_annotations()
    self.import_relations()


  def cleanup(self):
    shutil.rmtree(self.unpack_target_dir, ignore_errors=True)


  def create_source_map(self):
    filepath = os.path.join(self.unpack_target_dir, self.source_file)
    with jsonlines.open(filepath) as sources:
      for source in sources:
        self.source_map[source.get('sourceId')] = [source.get('sourceName'), source.get('directoryName')]


  def import_sources(self):
    filepath = os.path.join(self.unpack_target_dir, self.source_file)
    with jsonlines.open(filepath) as sources:
      for source in sources:
        self.create_source(source)


  def import_schemas(self):
    schema_filepath = os.path.join(self.unpack_target_dir, self.schemas_file)
    types_filepath = os.path.join(self.unpack_target_dir, self.atntypes_file)

    with jsonlines.open(schema_filepath) as schemas:
      for schema in schemas:
        try:
          self.project.create_annotation_schema(schema['name'])
        except HTTPError as e:
          if (e.response.status_code == HTTPStatus.CONFLICT):
            logger.warning(f'Schema {schema.get("name")} already exists. Skipping')
          else:
            raise e

    with jsonlines.open(types_filepath) as atn_types:
      for atn_type in atn_types:
        try:
          self.project.create_annotation_type(
            name=atn_type.get('name'),
            color=atn_type.get('color'),
            is_relation=atn_type.get('isRelation'),
            is_document_classification=atn_type.get('isDocumentClassification'),
            schema=atn_type.get('schemaName'))
        except HTTPError as e:
          if (e.response.status_code == HTTPStatus.CONFLICT):
            logger.warning(f'Annotation type {atn_type.get("name")} already exists. Skipping')
          else:
            raise e


  def import_layers(self):
    layers_filepath = os.path.join(self.unpack_target_dir, self.layers_file)
    with jsonlines.open(layers_filepath) as layers:
      for layer in layers:
        try:
          self.project.create_annotation_layer(
            name=layer.get('name'),
            is_gold=layer.get('isGoldSet'),
            description=layer.get('description')
          )
        except HTTPError as e:
          if (e.response.status_code == HTTPStatus.CONFLICT):
            logger.warning(f'Annotation type {layer.get("name")} already exists. Skipping')
          else:
            raise e


  def import_annotations(self):
    batch_size = 1000
    annotations_filepath = os.path.join(self.unpack_target_dir, self.annotations_file)

    batch = []

    def insert_batch(batch: List):
      created = self.project.create_bulk_annotations(batch, dedup=True)
      for atn in created:
        self.annotation_map[str(atn.get('clientId'))] = atn

    with jsonlines.open(annotations_filepath) as annotations:
      for annotation in annotations:
        source = self.source_map.get(annotation.get('sourceId'), None)
        if (source is None):
          logger.info(f'Skipping annotation for source {annotation.get("sourceId")}, source has not been imported.')
          continue

        sourceName = source[0]
        dirName = source[1]

        batch.append({
          'type': annotation.get('typeName'),
          'schema': annotation.get('schemaName'),
          'value': annotation.get('value'),
          'offsets': annotation.get('offsets'),
          'text_bounds': annotation.get('textBounds'),
          'image_bounds': annotation.get('imageBounds'),
          'client_id': annotation.get('id'),
          'layer': annotation.get('layerName'),
          'page': annotation.get('pageNumber'),
          'endPage': annotation.get('endPageNumber'),
          'source': sourceName,
          'directory': dirName,
          'project': self.project.id
        })
        if (len(batch) >= batch_size):
          insert_batch(batch)

    # Insert final batch
    if (len(batch) > 0):
      insert_batch(batch)


  def import_relations(self):
    batch_size = 1000
    relations_filepath = os.path.join(self.unpack_target_dir, self.relations_file)
    batch = []

    with jsonlines.open(relations_filepath) as relations:
      for rln in relations:
        batch.append({
          'annotations': [
            self.annotation_map.get(str(rln.get('predecessorId'))).get('id'),
            self.annotation_map.get(str(rln.get('successorId'))).get('id')
          ],
          'type': rln.get('typeName'),
          'schema': rln.get('schemaName'),
          'value': rln.get('value'),
          'project': self.project.id
        })
        if (len(batch) >= batch_size):
          self.project.create_bulk_relations(batch, dedup=True)

    # Insert final batch
    if (len(batch) > 0):
      self.project.create_bulk_relations(batch, dedup=True)


  def create_source(self, source: dict):
    self.source_map[source.get('sourceId')] = [source.get('sourceName'), source.get('directoryName')]
    try:
      if source['type'] == 'text':
        self.project.create_text_source(source['sourceName'], source['text'], source['directoryName'])
      elif source['type'] == 'pdf':
        pdf_filepath = os.path.join(self.unpack_target_dir, source['directoryName'], source['sourceName'])
        text_bounds = self.__find_source_bounds(source['sourceId'])
        if (text_bounds is None):
          logger.error(f'Unable to find text bounds for {source["sourceId"]}')

        self.project.create_pdf_source(
          pdf_filepath,
          source['sourceName'],
          source['directoryName'],
          ocr=False,
          sourceText=source['text'],
          textBounds=text_bounds['textBounds']
        )
    except HTTPError as e:
      if (e.response.status_code == HTTPStatus.CONFLICT):
        logger.warning(f'Source {source.get("directory")}/{source.get("sourceName")} already exists. Skipping')
      else:
        raise e


  def __find_entity_files(self):
    contents = os.listdir(self.unpack_target_dir)
    export_files = list(filter(lambda item: re.match('.*jsonl', item), contents))

    self.source_file = self.__find_file(export_files, '.*\.sources\.jsonl')
    self.bounds_file = self.__find_file(export_files, '.*\.text-bounds\.jsonl')
    self.annotations_file = self.__find_file(export_files, '.*\.annotations\.jsonl')
    self.layers_file = self.__find_file(export_files, '.*\.layers\.jsonl')
    self.relations_file = self.__find_file(export_files, '.*\.relations\.jsonl')
    self.schemas_file = self.__find_file(export_files, '.*\.schemas\.jsonl')
    self.atntypes_file = self.__find_file(export_files, '.*\.atntypes\.jsonl')

    if (self.source_file is None):
      raise Exception('Sources missing from export. Ensure to make the export request using includeSources=True.')
    if (self.bounds_file is None):
      raise Exception('Text Bounds missing from export. Ensure to make the export request using includeTextBounds=True.')
    if (self.schemas_file is None):
      raise Exception('Schemas missing from export. Ensure to make the export request using includeSchemas=True.')
    if (self.atntypes_file is None):
      raise Exception('Annotation Types missing from export. Ensure to make the export request using includeSchemas=True.')
    if (self.annotations_file is None):
      raise Exception('Annotations missing from export.')
    if (self.layers_file is None):
      raise Exception('Layers missing from export.')
    if (self.relations_file is None):
      raise Exception('Relations missing from export.')


  def __find_file(self, file_list: List[str], pattern: str):
    for filename in file_list:
      if (re.match(pattern, filename) is not None):
        return filename

    return None


  def __find_source_bounds(self, source_id: int):
    """Finds the source bounds of a source by iterating through the bounds file for the source id.

      *** Note: This is a highly inefficient v0.1 implementation ***
      The bounds file is redundantly iterated through every time.
      Perhaps the file should be pre-parsed, storing the byte offset of every source id to form
      an index?
    """
    filepath = os.path.join(self.unpack_target_dir, self.bounds_file)
    with jsonlines.open(filepath) as text_bounds:
      for bounds in text_bounds:
        if (bounds['sourceId'] == source_id):
          return bounds

    return None