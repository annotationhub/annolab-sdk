=========================================
AnnoLab - The Official Python AnnoLab SDK
=========================================

|Version|

This is the official python SDK for AnnoLab, the AI-first title production platform for aircraft and land.

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

Configure the sdk with your api key using one of the following three methods.

1. Create an instance of the SDK passing your api_key.

.. code-block:: python

    >>> from annolab import AnnoLab
    >>> lab = AnnoLab(api_key='YOUR_API_KEY')

2. Or set a global api key. All subsequent uses of the sdk will use this global key for authentication.

.. code-block:: python

    >>> import annolab
    >>> from annolab import AnnoLab
    >>>
    >>> annolab.api_key = 'YOUR_API_KEY'
    >>> lab = AnnoLab()

3. Or set the ``ANNOLAB_API_KEY`` environment variable. The sdk falls back to it when no key is passed or set globally.

.. code-block:: sh

    $ export ANNOLAB_API_KEY='YOUR_API_KEY'

.. code-block:: python

    >>> from annolab import AnnoLab
    >>> lab = AnnoLab()


Usage Examples
##############

Creating a project.
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    lab.create_project('My New Project')
    # OR
    lab.create_project(name='My New Project', owner_name='AnnoLab')

Getting an existing project.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    lab.find_project('My New Project')
    # OR
    lab.find_project(name='My New Project', owner_name='AnnoLab')

Creating a land abstract.
~~~~~~~~~~~~~~~~~~~~~~~~~

AOIs are used by Land AI to limit direct conveyance extractions.

.. code-block:: python

    project = lab.find_project('My Land Project')
    abstract = project.create_abstract(
      name='Garvin 12-3N-4W',
      aois=[{
        'state': 'OK',
        'county': 'Garvin',
        'section': '12',
        'township': '3N',
        'range': '4W'
      }],
      subdivisions=['Green Acres']
    )

    # Texas AOIs use block, abstract, and survey instead of range
    abstract = project.create_abstract(
      name='Midland 18-37',
      aois=[{
        'state': 'TX',
        'county': 'Midland',
        'section': '18',
        'block': '37',
        'township': 'T1S',
        'abstract': '123',
        'survey': 'T&P RR Co'
      }]
    )

Finding an existing land abstract by name.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    project = lab.find_project('My Land Project')
    abstract = project.find_abstract('Garvin 12-3N-4W')
    print(abstract.id, abstract.name, abstract.tags)

End-to-end land abstract workflow.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an abstract, upload a PDF, wait for processing, then print instruments.

See `Land Instrument <https://docs.annolab.ai/annotations-and-relations/land-instruments>`_ and `Conveyances <https://docs.annolab.ai/annotations-and-relations/conveyances>`_ in our docs for description of produced attributes.

.. code-block:: python

    from annolab import AnnoLab

    lab = AnnoLab(api_key='YOUR_API_KEY')

    project = lab.find_project('My Land Project')

    abstract = project.create_abstract(
      name='Garvin 12-3N-4W',
      aois=[{
        'state': 'OK',
        'county': 'Garvin',
        'section': '12',
        'township': '3N',
        'range': '4W'
      }],
      subdivisions=['Green Acres']
    )

    # OCR runs by default (the same default as project.create_pdf_source).
    # Pass ocr=False to extract the pdf's embedded text instead.
    result = abstract.upload_file(
      file='/path/to/deed.pdf',
      workflow='land_title'
    )

    # result.execution is None when the upload did not start a workflow.
    # wait_until_complete() is a no-op in that case.
    result.wait_until_complete()
    if result.execution:
      print(result.execution.status)

    abstract.populate_instruments()
    print(abstract.instruments)


Fetching an abstract's instruments and conveyance data.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    project = lab.find_project('My Land Project')
    abstract = project.find_abstract('Garvin 12-3N-4W')
    abstract.populate_instruments()
    print(abstract.instruments)

Creating a new text source.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Will be added to the "Uploads" directory by default.

.. code-block:: python

    project = lab.find_project('My New Project')
    project.create_text_source(name='New Source', text='Some text or tokens for annotation.')
    # Specifying a directory
    project.create_text_source(
      name='New Source',
      text='Some text or tokens for annotation.',
      directory='Uploads'
    )

Creating a new pdf source from a file.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Will be added to the "Uploads" directory by default.

.. code-block:: python

    project = lab.find_project('My New Project')
    project.create_pdf_source(file='/path/to/file')
    project.create_pdf_source(file='/path/to/file', name='custom_name.pdf', directory='Uploads')

    # Skip OCR and extract the pdf's embedded text instead
    project.create_pdf_source(file='/path/to/file', ocr=False)

    # You may also pass a filelike object or bytes. "name" is required when doing so.
    project.create_pdf_source(file=open('myfile.pdf', 'r+b'), name='myfile.pdf')

Creating a new pdf source from a web source.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    project = lab.find_project('My New Project')
    project.create_pdf_source_from_web(url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', name='mypdf.pdf')

Adding annotations.
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    project.create_annotations(
      source_name='New Source',
      annotations=[
          { 'type': 'one', 'value': 'value one', 'offsets': [0, 10]},
          { 'type': 'two', 'value': 'two', 'offsets': [10, 20] }
      ],
  )

Adding annotations with relations.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
