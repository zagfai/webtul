#!/usr/bin/python
# -*- coding: utf-8 -*-
""" webtul's setup file
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

from setuptools import setup
from webtul import __version__


setup(
  name="webtul",
  version=__version__,
  description="A set of web developing tools.",
  author="Zagfai",
  url="http://github.com/zagfai/webtul",
  license="MIT",
  packages=["webtul"],
  platforms=["any"],
)

