#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Task.
Including task server and task client.
Task module base on gevent.

A server should be started before clients connect.
Run "python -m webtul.task" to simply start a server.
And do the Client like this:
ipython
>> import webtul
>> taskclient = webtul.task.Task()
>> taskclient.put("msg body")
>> taskclient.get()
See more example from test.
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2015-06'

import time
import random
import hashlib
import logging
import zlib
import gevent
import json
import urlparse
import requests
import signal
from gevent.wsgi import WSGIServer
from gevent import queue as gevent_queue

from .utils import json_dumps


class TaskServer(object):
    """Task server.
    Run "python -m webtul.task" to simply start a server.
    """
    def __init__(self, addr=('localhost', 1606), backlog=None, secretkey=None,
        maxsize=0, queue=None, set=None, count=None, log=None):

        self.addr = addr
        self.backlog = backlog
        self.secretkey = secretkey
        self.maxsize = maxsize
        self.log = logging.getLogger('webtul.TaskServer') \
            if log is None else log
        self.server = WSGIServer(
            addr, self._application, log=None, backlog=self.backlog)
        self._init_dataset(queue, set, count)

    def _init_dataset(self, queue=None, set=None, count=None):
        if queue is None:
            self.task_queue = gevent_queue.Queue(maxsize=self.maxsize)
        if set is None:
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
                environ['query_dict'] = json.loads(_raw)
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
            yield ''
        else:
            try:
                _x = json_dumps(self.handler(environ))
                status = '200 OK'
                start_response(status, headers)
                yield _x
            except Exception, e:
                self.log.exception(e)
                status = '500 Server Error'
                start_response(status, headers)
                yield ''

        self.log.info("%s %s" %
            (environ.get('query_dict', {}).get('op'), status, ))

    def handler(self, environ):
        recv = environ['query_dict']
        if 'op' not in recv:
            return {"status": "no operation"}
        recv['op'] = recv['op'].upper()

        if recv['op'] == "PUT":
            self.st_put += 1
            body = "%s" % (recv['body'],)
            body_id = hashlib.md5(str(time.time()) + body).hexdigest()
            try:
                self.task_queue.put(
                    body_id + body, timeout = recv.get('timeout', 20))
            except gevent_queue.Full:
                return {"status": "full"}
            return {"status": "ok", "id": body_id}

        if recv['op'] == "GET":
            self.st_get += 1
            try:
                geted = self.task_queue.get(
                    timeout = int(recv.get('timeout', 60)))
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
    CLIENT_GID = hashlib.sha256("%s %s" %
        (time.time(), random.randint(0,1000000000))).hexdigest()
    logging.getLogger("requests").setLevel(logging.WARNING)

    def __init__(self, addr=('localhost', 1606), secretkey=None, log=None):
        self.addr = addr
        self.secretkey = secretkey
        self.log = logging.getLogger('webtul.Task') \
            if log is None else log
        self.endpoint = "http://%s:%s/" % addr
        self.req = lambda x: requests.post(self.endpoint, data=json_dumps(x))

    def put(self, body):
        req = self.req({'op': 'PUT', 'body': body})
        if req.status_code != 200:
            return None
        result = req.json()
        if result.get('status') != 'ok':
            return False
        return True

    def get(self, timeout=10):
        """get() -> {'id': 32-byte-md5, 'body': msg-body}"""
        req = self.req({'op': 'GET', 'timeout': timeout})
        if req.status_code != 200:
            return None
        result = req.json()
        if result.get('status') != 'ok':
            return False
        return result

    def done(self, id):
        req = self.req({'op': 'DONE', 'id': id})
        if req.status_code != 200:
            return None
        result = req.json()
        if result.get('status') != 'ok':
            return False
        return True

    def get_air():
        # TODO
        pass

    def count(self):
        return self.req({'op': 'COUNT'}).json()



def task_server():
    import argparse
    parser = argparse.ArgumentParser(description="Easy start task server")
    parser.add_argument("-H", "--host", default="localhost",
        help = "Host name like default localhost.")
    parser.add_argument("-p", "--port", default=1606,
        help = "Service port.")
    parser.add_argument("-lf", "--log-file", default="",
        help = "Specify a file to log to, default output to stdout.")
    args = parser.parse_args()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # reg singals
    def _log_reopen():
        logger.info("Reopening log file.")
        if args.log_file:
            loghdl = logging.FileHandler(args.log_file)
        else:
            loghdl = logging.StreamHandler()

        dlf = logging.Formatter(
                    '[%(levelname).1s %(asctime)s %(name)s '
                    '%(filename)s:%(lineno)d] %(message)s',
                    '%Y-%m-%d %H:%M:%S')
        loghdl.setFormatter(dlf)
        logger.addHandler(loghdl)
        logger.debug("Log, new handler.")
        if hasattr(logger, 'handlers'):
            # To let the files reopen themselves
            for hdl in logger.handlers[:]:
                if isinstance(hdl, logging.FileHandler) and hdl != loghdl:
                    hdl.close()
                    logger.removeHandler(hdl)
        logger.info("Reopened log file.")
    def _shutdown():
        logger.warning("Server shutting down.")
        taskserver.server.stop(timeout=10)
        logger.warning("Shutted.")
        exit(signal.SIGTERM)
    gevent.signal(signal.SIGUSR2, _log_reopen)
    gevent.signal(signal.SIGQUIT, _shutdown)
    gevent.signal(signal.SIGTERM, _shutdown)
    gevent.signal(signal.SIGINT, _shutdown)

    _log_reopen()
    taskserver = TaskServer(
        addr=(args.host, args.port), backlog=None, secretkey=None, maxsize=0,
        queue=None, set=None, count=None, log=None)
    logger.warning("Server started.")
    taskserver.loop()


if __name__ == '__main__':
    task_server()

