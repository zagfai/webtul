#!/usr/bin/python
# -*- coding: utf-8 -*-
"""utils functions
"""
__author__ = 'Zagfai'
__version__=  '2013-09-03'

import json
import datetime


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
    """Decorator for browser. Only for webpy
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

