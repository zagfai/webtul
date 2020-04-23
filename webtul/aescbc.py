#!/usr/bin/python
# -*- coding: utf-8 -*-
""" AES crypto, for easy use to encrypt and decrypt short data.
"""
__author__ = 'Zagfai'
__date__ = '2018-10'


import base64
from Crypto import Random
from Crypto.Cipher import AES


class Base64AESCBC(object):
    def __init__(self, key):
        self.key = key[:32] + '\x00' * (32 - len(key))

    def encrypt(self, iv, raw):
        if type(raw) is bytes:
            raw = raw.decode('utf8')
        raw = self._pad_16(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, iv[:16])
        return cipher.encrypt(raw)

    def b64encrypt(self, iv, raw):
        return base64.b64encode(self.encrypt(iv, raw)).decode('utf8')

    def decrypt(self, iv, enc):
        cipher = AES.new(self.key, AES.MODE_CBC, iv[:16])
        return self._unpad(cipher.decrypt(enc)).decode('utf8')

    def b64decrypt(self, iv, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(iv, enc)

    def _pad_16(self, s):
        lfsize = 16 - len(s) % 16
        return s + lfsize * chr(lfsize)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


def test_easy(tx):
    key = str(bytearray.fromhex(
        '31ac6364261dadc8faeb2dcb72a88b429ccee4c89d6f8aa8fc02a95762c1b2f0'))
    pc = Base64AESCBC(key)
    iv = Random.new().read(AES.block_size)
    iv = '0' * 17
    print('iv:', iv)
    e = pc.b64encrypt(iv, tx)
    d = pc.b64decrypt(iv, e)
    print("RAW.:", len(tx), tx)
    print(u"加密:", len(e), e)
    print(u"解密:", len(d), d)
    print(type(tx), type(d))
    if tx != d:
        raise Exception('Hi')


if __name__ == '__main__':
    tx = 'Hello ' * 10
    test_easy(tx)
