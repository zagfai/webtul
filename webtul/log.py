#!/usr/bin/python
# -*- coding: utf-8 -*-
""" High-level logging abstract, make it easy to log.
Sometimes we need details of an error, so log.trackback() makes it easy.
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2014-01'

import os
import re
import logging
from time import sleep
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import time as tt
from threading import Timer

DEFAULT_LOG_FORMAT = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
            '%Y-%m-%d %H:%M:%S')
FILE_ROTATE_TIMER = None
RE_FILENAME = re.compile('^\d{4}-[01]\d-[0123]\d$')


def get_logger(name=None):
    def _traceback_wrap(self):
        def traceback():
            import traceback as tb
            for l in tb.format_exc().split('\n'):
                l and self.critical(l)
        return traceback

    def _prefix_wrap(self):
        def prefix(name=None):
            logger = self.getChild(name)
            logger.traceback = _traceback_wrap(logger)
            return logger
        return prefix

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.traceback = _traceback_wrap(logger)
    logger.prefix = _prefix_wrap(logger)
    return logger

class LogServer():
    """LoggingServer, for multiprocessing or distributing."""
    def __init__(self):
        # TODO
        pass

def logtoserv():
    # TODO
    pass

def save(filename, level='INFO', name=None):
    filename = os.path.abspath(filename)
    path, _ = os.path.split(filename)
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == 17:
            pass
    logger = get_logger(name)
    fh = logging.FileHandler(filename)
    fh.setLevel(getattr(logging, level))
    fh.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(fh)

def rotate_save(filename, level='INFO', name=None, backup_count=None):
    def rotate_daemon(path, filename, logger, fhandler=None):
        while dt.now().hour != 0 and fhandler:
            sleep(1) # make the following do after midnight

        logname = '%s.%s' % (filename, dt.now().date())
        nfhlr = logging.FileHandler(os.path.join(path, logname))
        nfhlr.setLevel(getattr(logging, level))
        nfhlr.setFormatter(DEFAULT_LOG_FORMAT)
        logger.addHandler(nfhlr)
        if fhandler is not None:
            logger.removeHandler(fhandler)

        # start the next
        next_midnight = dt.combine(dt.now().date()+td(1),tt(0,0))
        next_time = (next_midnight - dt.now()).seconds
        tmr = Timer(next_time, rotate_daemon, (path, filename, logger, nfhlr))
        tmr.daemon = True
        tmr.start()

        # trush old logs
        if backup_count:
            bkdate = set([(dt.now()-td(t)).strftime('%Y-%m-%d')
                    for t in xrange(backup_count+1)])
            filelist = os.walk(path).next()[2]
            trush_file = []
            for xfile in filelist:
                splited_list = xfile.rsplit('.', 1)
                if len(splited_list) != 2:
                    continue
                spname, spdate = splited_list
                if filename != spname:
                    continue
                if not re.match(RE_FILENAME, spdate):
                    continue
                if spdate in bkdate:
                    continue
                trush_file.append(xfile)
            for i in trush_file:
                os.remove(os.path.join(path, i))

    filename = os.path.abspath(filename)
    path, filename = os.path.split(filename)
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == 17:
            pass
    logger = get_logger(name)
    rotate_daemon(path, filename, logger)

def display(level='DEBUG'):
    """display(level='DEBUG') forwards logs to stdout"""
    logger = get_logger()
    sh = logging.StreamHandler()
    sh.setLevel(getattr(logging, level))
    sh.setFormatter(DEFAULT_LOG_FORMAT)
    logger.addHandler(sh)


if __name__ == '__main__':
    save('abc.log')
    rotate_save('abc.log', backup_count=2)
    display()
    a = get_logger()
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
