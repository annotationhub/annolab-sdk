class Project:

  @staticmethod
  def post_create():
    return 'v1/project/create'


  @staticmethod
  def get_group_project(groupName: str, projectName: str):
    return f'v1/project/{groupName}/{projectName}'


  @staticmethod
  def get_using_id(id: int):
    return f'v1/project/{id}'


class Export:

  @staticmethod
  def post_export_project():
    return 'v1/export/project'


class Directory:

  @staticmethod
  def post_create():
    return 'v1/directory/create'


class Annotation:

  @staticmethod
  def post_create():
    return 'v1/annotation/create'

  @staticmethod
  def post_bulk_create():
    return 'v1/annotation/bulk-create'


class AnnotationType:

  @staticmethod
  def post_create():
    return 'v1/annotation-type/create'


class AnnotationSchema:

  @staticmethod
  def post_create():
    return 'v1/schema/create'


class AnnotationRelation:

  @staticmethod
  def post_create():
    return 'v1/relation/create'


  @staticmethod
  def post_bulk_create():
    return 'v1/relation/bulk-create'


class AnnotationLayer:

  @staticmethod
  def post_create():
    return 'v1/layer/create'


class Source:

  @staticmethod
  def get_source_by_id(source_ref_id: int):
    return f'v1/source/{source_ref_id}'


  @staticmethod
  def get_source_by_path(owner_name: str, project_name: str, directory_name: str, source_ref_name: str):
    return f'v1/source/{owner_name}/{project_name}/{directory_name}/{source_ref_name}'


  @staticmethod
  def post_create_text():
    return 'v1/source/create-text'


  @staticmethod
  def post_initialize_pdf():
    return 'v1/source/init-pdf'


  @staticmethod
  def post_create_pdf():
    return 'v1/source/create-pdf'


  @staticmethod
  def post_annotations(owner_name: str, project_name: str, directory_name: str, source_ref_name: str):
    return f'v1/source/{owner_name}/{project_name}/{directory_name}/{source_ref_name}/annotations'


  @staticmethod
  def delete_using_name(owner_name: str, project_name: str, directory_name: str, source_ref_name: str):
    return f'v1/source/{owner_name}/{project_name}/{directory_name}/{source_ref_name}'


  @staticmethod
  def delete_using_id(id: int):
    return f'v1/source/{id}'


class ApiKey:
  @staticmethod
  def get_api_key_info():
    return 'v1/api-key/info'