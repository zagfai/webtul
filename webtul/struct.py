#!/usr/bin/python
# -*- coding: utf-8 -*-
""" Struct tools
Struct is same as Storage object in webpy.
"""
__author__ = 'edited from webpy'


class Struct(dict):
    """
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`.

        >>> o = storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Struct ' + dict.__repr__(self) + '>'


if __name__ == '__main__':
    a = Struct({'a': 'b', 3: 2, 3: 'a', 'b': 3})  # NOQA
    print(a)
    print(a.a)
    print(a.b)
    print(a[3])
    print(3 in a)
