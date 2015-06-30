#!/usr/bin/python
# -*- coding: utf-8 -*-
""" webtul's setup file
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

from setuptools import setup
from webtul import __version__


setup(
  name = "webtul",
  version = __version__,
  keywords = ('web', 'lib', 'library', 'toolkit'),
  description = "A set of web/task developing tools.",
  author = "Zagfai",
  author_email = 'zagfai@gmail.com',
  url = "http://github.com/zagfai/webtul",
  license = "MIT License",
  install_requires = ["requests", "gevent"],
  packages = ["webtul"],
  platforms = ["any"],
)

