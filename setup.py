#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
  name = 'annolab',
  version='0.1.3',
  packages = find_packages(),
  author='AnnoLab',
  maintainer='Luke Simkins; Grant DeLozier',
  author_email='luke@annolab.ai',
  url='https://github.com/lsimkins/annolab-sdk',
  license='Apache',
  description='Official SDK for the AnnoLab Platform',
  long_description=open('README.rst').read(),
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)