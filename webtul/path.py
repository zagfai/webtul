#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Path functions
"""
__author__ = 'Zagfai'
__date__ = '2018-03'


import sys
from os import path


def apath(x):
    """Return absolutely path of relative path from the root"""
    return path.join(
            path.dirname(
                path.abspath(
                    sys.modules['__main__'].__file__)), x)
