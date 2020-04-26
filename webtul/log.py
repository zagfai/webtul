#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Log Config
"""
__author__ = 'Zagfai'
__date__ = '2018-06'


SANIC_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format':
                '%(levelname)s [%(asctime)s %(name)s:%(lineno)d] %(message)s',
            'datefmt': '%y%m%d %H:%M:%S',
        },
        "access": {
            "format": "VISIT [%(asctime)s %(host)s]: " +
                      "%(request)s %(message)s %(status)d %(byte)d",
            'datefmt': '%y%m%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': True
        },
        'sanic.access': {
            'level': 'INFO',
            'handlers': ['access_console'],
            'propagate': False
        },
    }
}
