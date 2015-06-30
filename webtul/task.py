#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Task.
Including task server and task client.
A server should be started before clients connect.
Task module base on gevent.
See more example from test.
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2015-06'

import sys
import time
import hashlib
import logging
import zlib
import gevent
import json
import urlparse
from gevent.wsgi import WSGIServer
from gevent import queue as gevent_queue
import signal

from .utils import json_dumps


class TaskServer(object):
    """Task server.
    Run "python -m webtul.task" to simply start a server.
    """
    def __init__(self, addr=('', 1606), backlog=None, secretkey=None, size=0,
        queue=None, _set=None, count=None, log=None):

        self.addr = addr
        self.backlog = backlog
        self.secretkey = secretkey
        self.log = logging.getLogger('Webtul.TaskServer') \
            if log is None else log
        self.server = WSGIServer(
            addr, self._application, log = 'default', backlog = self.backlog)
        self._init_dataset(queue, _set, count)

    def _init_dataset(self, queue=None, _set=None, count=None):
        if queue is None:
            self.task_queue = gevent_queue.Queue(maxsize=0)
        if _set is None:
            self.on_airs = dict()
        if count is None:
            self.st_done_task_count = 0
            self.st_put = 0
            self.st_get = 0
            self.st_got = 0
            self.st_done = 0
            self.st_get_air = 0

    def _application(self, environ, start_response):
        headers = [('Content-Type', 'text/json')]

        if environ.get('HTTP_REQUEST_ENCODE') == 'gzip':
            gzipd = zlib.decompress
        else:
            gzipd = lambda x: x

        try:
            _raw = gzipd(environ['wsgi.input'].read())
            if _raw:
                environ['query_dict'] = json.loads()
            else:
                environ['query_dict'] = {}
            qd = environ['query_dict']
            for k,v in urlparse.parse_qsl(environ['QUERY_STRING']):
                if k not in qd:
                    qd[k] = v
        except Exception, e:
            self.log.exception(e)
            status = '400 Bad Request'
            start_response(status, headers)
            return ['']

        try:
            _x = [json_dumps(self.handler(environ))]
            status = '200 OK'
            start_response(status, headers)
            return _x
        except Exception, e:
            self.log.exception(e)
            status = '500 Server Error'
            start_response(status, headers)
            return ['']

    def handler(self, environ):
        recv = environ['query_dict']

        if 'op' not in recv:
            return {"status": "server error"}

        if recv['op'] == "PUT":
            self.st_put += 1
            body_id = hashlib.md5(str(time.time()) + recv['body']).hexdigest()
            try:
                self.task_queue.put(
                    body_id + recv['body'], timeout = recv.get('timeout', 20))
            except gevent_queue.Full:
                return {"status": "full"}
            return {"status": "ok", "id": body_id}

        if recv['op'] == "GET":
            self.st_get += 1
            try:
                geted = self.task_queue.get(timeout=recv.get('timeout', 60))
            except gevent_queue.Empty:
                return {"status": "empty"}
            self.on_airs[geted[:32]] = geted[32:]
            self.st_got += 1
            return {"status": "ok", "body": geted[32:], "id": geted[:32]}

        if recv['op'] == "DONE":
            self.st_done += 1
            try:
                self.on_airs.pop(recv['id'])
                self.st_done_task_count += 1
            except KeyError:
                return {"status": "nonexistent"}
            return {"status": "ok"}

        if recv['op'] == "GET-AIR":
            self.st_get_air += 1
            try:
                datatuple = self.on_airs.popitem()
            except KeyError:
                datatuple = None
            if datatuple is None:
                return {"status": "empty"}
            return {"status": "ok", "id": datatuple[0], "body": datatuple[1]}

        if recv['op'] == "COUNT":
            return {
                "status": "ok",
                "done": self.st_done_task_count,
                "onair": len(self.on_airs),
                "remain": self.task_queue.qsize(),
                "put": self.st_put,
                "get": self.st_get,
                "got": self.st_got,
                "done": self.st_done,
                "get-air": self.st_get_air,
            }


    def loop(self):
        return self.server.serve_forever()



class Task(object):
    """Task client. """
    pass


def task_server():
    PORT = 1606
    DEFAULT_LOG_FORMAT = logging.Formatter(
                '[%(levelname).1s %(asctime)s %(name)s - %(filename)s:%(lineno)d] %(message)s',
                '%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('Webtul')
    logger.setLevel(logging.INFO)

    # reg singals
    def _log_reopen():
        loghdl = logging.FileHandler("/data/log/webtul.task.log")
        loghdl.setFormatter(DEFAULT_LOG_FORMAT)
        logger.addHandler(loghdl)
        if hasattr(logger, 'handlers'):
            # To let the files reopen themselves
            for hdl in logger.handlers[:]:
                if isinstance(hdl, logging.FileHandler) and hdl != loghdl:
                    hdl.close()
                    logger.removeHandler(hdl)
    gevent.signal(signal.SIGUSR2, _log_reopen)
    _log_reopen()
    def shutdown():
        logger.warning("Server shutting down.")
        taskserver.server.stop(timeout=60)
        logger.warning("Shutted.")
        exit(signal.SIGTERM)
    gevent.signal(signal.SIGQUIT, shutdown)
    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)


    taskserver = TaskServer(
        addr=('', PORT), backlog=None, secretkey=None, size=0,
        queue=None, _set=None, count=None, log=None)
    logger.warning("Server started.")
    taskserver.loop()


if __name__ == '__main__':
    task_server()

