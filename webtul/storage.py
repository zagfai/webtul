#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" File tools
"""
__author__ = 'Zagfai'
__date__ = '2020-04'


from os import SEEK_END, SEEK_SET


def get_last_n_line_from_file(f, n):
    """ Would be a big cost if n is too big.
        Return: list of string order as tail.
    """
    if n == 0:
        return []

    chunk_size = 256
    strs = []
    n_count = 0

    f.seek(0, SEEK_END)
    size = f.tell()

    for pos in range(chunk_size, size, chunk_size):
        f.seek(-pos, SEEK_END)
        chunk = str(f.read(chunk_size), encoding='utf-8')
        n_count += chunk.count('\n')
        strs.append(chunk)
        if n_count >= n:
            break
    else:
        f.seek(0, SEEK_SET)
        return str(f.read(), encoding='utf-8').splitlines()[-n:]

    return ''.join(reversed(strs)).splitlines()[-n:]


if __name__ == "__main__":
    import pprint
    pprint.pprint(get_last_n_line_from_file(open('storage.py', 'rb'), 50))
    pprint.pprint(get_last_n_line_from_file(open('storage.py', 'rb'), 5))
    pprint.pprint(get_last_n_line_from_file(open('storage.py', 'rb'), 1))
    pprint.pprint(get_last_n_line_from_file(open('storage.py', 'rb'), 0))
