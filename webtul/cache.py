#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Cache using redis
Or could use to store some temp data.
Basically, implement
    key
        get
        set
    queue (list)
        get
        set
"""
__author__ = 'Zagfai'
__date__ = '2016-03'
__license__ = 'MIT'

import logging
from redis import Redis


class Cache(Redis):
    def __init__(self, host='127.0.0.1', port=6379, db=0, pwd=''):
        self.c = Redis(host=host, port=port, db=db, password=pwd)
        logging.info("New a cache server.")

    def add_task(self, queue_id, content):
        return self.c.lpush(queue_id, *content)

    def get_task(self, queue_id):
        return self.c.rpop(queue_id)

    def hset(self, key, field, value, expire=None):
        res = self.c.hset(key, field, value)
        if expire > 0:
            self.c.expire(key, expire)
        return res

    def hget(self, key, field):
        return self.c.hget(key, field)

    def hdel(self, key, field):
        return self.c.hdel(key, field)

    def hgetall(self, key):
        return self.c.hgetall(key)

    def add_key(self, key, value):
        return self.c.set(key, value)

    def add_exp_key(self, key, value, ex):
        "Expired in seconds"
        return self.c.set(key, value, ex)

    def get_key(self, key):
        return self.c.get(key)

if __name__ == '__main__':
    cache = Cache()
    print cache.add_task('abc', ['13 21', '21'])
    print cache.get_task('abc')
    print cache.get_task('abc')

