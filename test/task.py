#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Test suit for Task
"""
__author__ = 'Zagfai'
__license__ = 'MIT@2015-06'

import threading

from webtul import task


def test_task_put_get_done_count():
    thserv = threading.Thread(target=task.task_server)
    thserv.start()

    tc = task.Task()
    print tc.get(3)
    print tc.put('hello, test')
    res = tc.get()
    print res
    print tc.done(res['id'])
    print tc.count()


if __name__ == '__main__':
    test_task_put_get_done_count()

