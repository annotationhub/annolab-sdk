=========================================
AnnoLab - The Official Python AnnoLab SDK
=========================================

|Version|

This is the official python SDK for AnnoLab, the ML platform for NLP projects.

`AnnoLab Website <https://annolab.ai>`__

.. |Version| image:: http://img.shields.io/pypi/v/annolab.svg?style=flat
    :target: https://pypi.python.org/pypi/annolab/
    :alt: Version

Getting Started
---------------
Assuming that you have Python and ``virtualenv`` installed, set up your environment and install the required dependencies like this or you can install the library using ``pip``:

.. code-block:: sh

    $ virtualenv venv
    $ . venv/bin/activate
    $ python -m pip install annolab


Using the AnnoLab SDK
---------------------

To get started, ensure you have an annolab account at `<https://app.annolab.ai/signup>`__ and have created an API Key.
Instructions for creating an API Key may be found at `<https://docs.annolab.ai/>`__.

Configure the sdk with your api key using one of the following two methods.

1. Create an instance of the SDK passing your api_key.

.. code-block:: python

    >>> from annolab import Annolab
    >>> lab = AnnoLab(api_key='YOUR_API_KEY')

2. Or set a global api key. All subsequent uses of the sdk will use this global key for authentication.

.. code-block:: python

    >>> import annolab
    >>> from annolab import Annolab
    >>>
    >>> annolab.api_key = 'YOUR_API_KEY'
    >>> lab = AnnoLab()


Usage Examples
##############

Creating a project.

.. code-block:: python

    lab.create_project('My New Project')
    # OR
    lab.create_project(name='My New Project', owner_name='AnnoLab')

Getting an existing project.

.. code-block:: python

    lab.find_project('My New Project')
    # OR
    lab.find_project(name='My New Project', owner_name='AnnoLab')

Creating a new text source. Will be added to the "Uploads" directory by default.

.. code-block:: python

    project = lab.find_project('My New Project')
    project.create_text_source(name='New Source', text='Some text or tokens for annotation.')
    # Specifying a directory
    project.create_text_source(
      name='New Source',
      text='Some text or tokens for annotation.',
      directory='Uploads'
    )

Creating a new pdf source from a file. Will be added to the "Uploads" directory by default.

.. code-block:: python

    project = annolab.find_project('My New Project')
    project.create_pdf_source(file='/path/to/file')
    project.create_pdf_source(file='/path/to/file', name='custom_name.pdf', directory='Uploads')

    # You may also pass a filelike object or bytes. "name" is required when doing so.
    project.create_pdf_source(file=open('myfile.pdf', 'r+b'), name='myfile.pdf')

Creating a new pdf source from a web source.

.. code-block:: python

    project = annolab.find_project('My New Project')
    project.create_pdf_source_from_web(url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', name='mypdf.pdf')

Adding annotations.

.. code-block:: python

    project.create_annotations(
      source_name='New Source',
      annotations=[
          { 'type': 'one', 'value': 'value one', 'offsets': [0, 10]},
          { 'type': 'two', 'value': 'two', 'offsets': [10, 20] }
      ],
  )

Adding annotations with relations.

.. code-block:: python

    project.create_annotations(
      source_name='New Source',
      annotations=[
          { 'clientId': 1, 'type': 'one', 'value': 'value one', 'offsets': [0, 10]},
          { 'clientId': 2, 'type': 'two', 'value': 'two', 'offsets': [10, 20] }
      ],
      relations=[
        { 'annotations': [1, 2] }
      ]
  )

Exporting a project.

.. code-block:: python

    project.export(filepath='/path/to/outfile.zip')
    
    # With options
    project.export(
      filepath='/path/to/outfile.zip',
      source_ids=[1,2,3],
      layers=['GoldSet'],
      include_schemas=True,
      include_sources=True
    )