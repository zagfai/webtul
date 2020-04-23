#!/usr/bin/python
# -*- coding: utf-8 -*-
""" String Lib base on string of Python
And make more useful functions
For Python 3
"""
__author__ = 'Zagfai'
__date__ = '2018-01'

import re
import time
import hashlib
import random
import string


_STR_LD = string.ascii_letters + string.digits


def make_62_str(byte=32):
    return ''.join(random.choice(_STR_LD) for i in range(byte))


def make_digits_str(byte=32, zero_start=True):
    if zero_start:
        return ''.join(random.choice(string.digits) for i in range(byte))
    else:
        ds = random.choice('123456789')
        ds += ''.join(random.choice(string.digits) for i in range(byte-1))
        return ds


def make_16_str(byte=32):
    """It is faster than make_enc_key..."""
    return hashlib.md5(repr(time.time()).encode("utf8")).hexdigest()


def base36encode(number, alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Converts an integer to a base36 string."""
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    base36 = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < len(alphabet):
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36

    return sign + base36


def base36decode(number):
    return int(number, 36)


def lcs_length(a, b):
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            table[i][j] = (
                table[i - 1][j - 1] + 1 if ca == cb else
                max(table[i][j - 1], table[i - 1][j]))
    return table[-1][-1]


def is_email(email):
    r = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    return r.match(email)


if __name__ == '__main__':
    # print(make_16_str())
    print(make_62_str())
    print(base36encode(999999999))
    print(base36decode('aQF8AA0006EH'))
    print(make_digits_str())
    print(make_digits_str(10, False))
    print(lcs_length('12345', '54321'))
    print(lcs_length('11111', '55555'))
    print(lcs_length('我111我11', '5我我5555'))
    print(lcs_length('我111我1你你1', '5我我你我你5555'))
    print(lcs_length('1'*1000, '1'*1000))
    print(is_email('zaak@yy'))
    print(is_email('za.ak@yy.com'))
    print(is_email('za.a:k@yy.com'))
    print(is_email('zaak@yy.com'))
