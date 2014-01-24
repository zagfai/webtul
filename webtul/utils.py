#!/usr/bin/python
# -*- coding: utf-8 -*-
"""utils functions
"""
__author__ = 'Zagfai'
__version__=  '2013-09-03'

import json
import datetime
import hashlib


def json_dumps(obj):
    class Encoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, datetime.date):
                return obj.strftime('%Y-%m-%d')
            elif isinstance(obj, datetime.time):
                return obj.strftime('%H:%M:%S')
            else:
                return json.JSONEncoder.default(self, obj)
    return json.dumps(obj, cls=Encoder,
                      ensure_ascii=False, encoding='utf8')

def recur(obj, type_func_tuple_list=()):
    '''recuring dealing an object'''
    for obj_type, func in type_func_tuple_list:
        if type(obj) == type(obj_type):
            return func(obj)
    # by default, we wolud recurring list, tuple and dict
    if isinstance(obj, list) or isinstance(obj, tuple):
        n_obj = []
        for i in obj:
            n_obj.append(recur(i))
        return n_obj if isinstance(obj, list) else tuple(obj)
    elif isinstance(obj, dict):
        n_obj = {}
        for k,v in obj.items():
            n_obj[k] = recur(v)
        return n_obj
    return obj

def browser_cache(seconds):
    """Decorator for browser cache. Only for webpy
    @browser_cache( seconds ) before GET/POST function.
    """
    import web
    def wrap(f):
        def wrapped_f(*args):
            last_time_str = web.ctx.env.get('HTTP_IF_MODIFIED_SINCE', '')
            last_time = web.net.parsehttpdate(last_time_str)
            now = datetime.datetime.now()
            if last_time and\
                    last_time + datetime.timedelta(seconds = seconds) > now:
                web.notmodified()
            else:
                web.lastmodified(now)
                web.header('Cache-Control', 'max-age='+str(seconds))
            yield f(*args)
        return wrapped_f
    return wrap

class _Bighash(object):
    """hash big files, or dataflow, iter~!
    Make the hash more safty.
    Usage:
    bighash.md5(open('xxx')).hexdigest()
    bighash.sha('hello').hexdigest()
    """
    algos = hashlib.algorithms
    def __init__(self):
        pass
    def __getattr__(self, attr):
        attrfunc = hashlib.__getattribute__(attr)
        if attr not in self.algos:
            return attrfunc
        def hashfunc(stream):
            d = attrfunc()
            if type(stream) is file:
                attr = iter(lambda:attr.read(4096), b'')
            for buf in stream:
                d.update(buf)
            return d
        return hashfunc
bighash = _Bighash()


if __name__ == '__main__':
    from hashlib import md5, sha1
    print bighash.md5(open('/home/zagfai/Desktop/try.c.out')).hexdigest()
    print md5(open('/home/zagfai/Desktop/try.c.out').read()).hexdigest()
    print bighash.sha1(open('/home/zagfai/Desktop/try.c.out')).hexdigest()
    print sha1(open('/home/zagfai/Desktop/try.c.out').read()).hexdigest()
    print bighash.md5('hello, crypto').hexdigest()
    print md5('hello, crypto').hexdigest()

