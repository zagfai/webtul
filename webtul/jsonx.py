#!/usr/bin/python
# -*- coding: utf-8 -*-
""" JSON Lib
"""
__author__ = 'Zagfai'
__date__ = '2018-01'


import json
import logging
from datetime import time, date, datetime
from decimal import Decimal


class NormalEncoder(json.JSONEncoder):
    """A normal encoder of JSON written by Zagfai with widely used in some
    projects, I believe this would solve most problem that would be meet.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            retobj = obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            retobj = obj.strftime('%Y-%m-%d')
        elif isinstance(obj, time):
            retobj = obj.strftime('%H:%M:%S')
        elif isinstance(obj, Decimal):
            try:
                if obj % 1 == 0:
                    retobj = int(obj)
                else:
                    retobj = float(obj)
            except Exception as exception:
                logging.error("Please solve json problem %s", str(exception))
                retobj = str(obj)
        else:
            retobj = json.JSONEncoder.default(self, obj)

        return retobj


def dumps(obj, **kwargs):
    """JSON dumps function"""
    return json.dumps(obj, cls=NormalEncoder, **kwargs)


def loads(jsonstr, **kwargs):
    """JSON loads function"""
    return json.loads(jsonstr, **kwargs)


def test():
    """Test function"""
    testcase = loads('''{"A":["B", "C", {"D":["E", "F"], "I": 123, "J": 321.0,
        "K": null, "L": true}],"M": false, "O": null,
        "P": "2015-12-03 11:11:11"}''')

    print(testcase)

    testcase['Q'] = Decimal('1')
    testcase['R'] = Decimal('1.01')
    testcase['S'] = datetime.now()
    testcase['T'] = Decimal('nan')

    print(dumps(testcase))


if __name__ == '__main__':
    test()
