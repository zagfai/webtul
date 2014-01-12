#!/usr/bin/python
# -*- coding: utf-8 -*-
""" High-level logging abstract, make it easy to log.
Sometimes we need details of an error, so log.trackback() makes it easy.
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

import os
import logging
from datetime import datetime as dt


DEFAULT_LOG_FORMAT = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            '%Y-%m-%d %H:%M:%S')

class LogServer():
    """LoggingServer, for multiprocessing or distributing."""
    def __init__(self):
        pass

def get_logger(name=None):
    def _traceback_wrap(self):
        def traceback():
            import traceback as tb
            for l in tb.format_exc().split('\n'):
                len(l) and self.critical(l)
        return traceback

    def _prefix_wrap(self):
        def prefix(name=None):
            logger = self.getChild(name)
            logger.traceback = _traceback_wrap(logger)
            return logger
        return prefix

    logger = logging.getLogger(name)
    logger.traceback = _traceback_wrap(logger)
    logger.prefix = _prefix_wrap(logger)
    return logger

def savefile(pathfile, level='INFO', name=None):
    try:
        path, filename = os.path.split(pathfile)
        try:
            os.makedirs(path)
        except OSError, e:
            if e.errno == 17:
                pass
        logger = get_logger(name)
        filename = pathfile + '.log.%s'%dt.now().date()
        fh = logging.FileHandler(filename)
        fh.setLevel(getattr(logging, level))
        fh.setFormatter(DEFAULT_LOG_FORMAT)
        logger.addHandler(fh)
    except Exception, e:
            return False, str(e)
    return True, ""

def logtoserv():
    # TODO
    pass

def display(level='DEBUG'):
    """display(level='DEBUG') forwards logs to stdout"""
    try:
        logger = get_logger()
        sh = logging.StreamHandler()
        sh.setLevel(getattr(logging, level))
        sh.setFormatter(DEFAULT_LOG_FORMAT)
        logger.addHandler(sh)
    except Exception, e:
        return False, str(e)
    return True, ""


if __name__ == '__main__':
    a = savefile('abc')
    a.info('321')

    b = get_logger('child.son')
    b.info('432')
    b.prefix('aa').info('321')

    try:
        raise Exception('..')
    except:
        a.traceback()

    c = b.prefix('daughter')
    c.warning('me')
