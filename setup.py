#!/usr/bin/python
# -*- coding: utf-8 -*-
""" webtul's setup file
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

from setuptools import setup

version = [i for i in open("webtul/__init__.py").readlines() if i.startswith("__version__")][0]
__version__ = ''
exec(version)

setup(
  name="webtul",
  version=__version__,
  keywords=['web', 'lib', 'library', 'toolkit'],
  description="A set of web/task developing tools.",

  author="Zagfai",
  author_email='zagfai@gmail.com',
  url="http://github.com/zagfai/webtul",
  license="MIT License",
  install_requires=[
      'pycrypto',
      'aiomysql',
      'aioimaplib',
      'aiosmtplib',
      'sanic',
      'Pillow',
      'websocket-client'],
  packages=["webtul"],
  # packages = find_packages(),
  python_requires='>=3',
  platforms=["any"],
)
