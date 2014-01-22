#!/usr/bin/python
# -*- coding: utf-8 -*-
""" webtul's setup file
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

from setuptools import setup, find_packages


setup(
  name="webtul",
  version="0.2",
  description="A set of web developing tools.",
  author="Zagfai",
  url="http://github.com/zagfai/webtul",
  license="MIT",
  packages= find_packages(),
  scripts=["webtul"],
)

