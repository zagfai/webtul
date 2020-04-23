#!/usr/bin/python
# -*- coding: utf-8 -*-
""" RSA module
Work with Python3
"""
__author__ = 'Zagfai'
__date__ = '2017-03'

import base64
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA as crsa
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5


class RSA(object):
    """RSA encrypt/decrypt module"""

    random_generator = Random.new().read

    def __init__(self, privk=None, pubk=None):
        self.privk = privk
        self.pubk = pubk

    def load_private_key_from_file():
        # TODO
        pass

    def load_public_key_from_file():
        # TODO
        pass

    def encrypt(self, content):
        if type(content) is str:
            content = content.encode('utf8')
        rsakey = crsa.importKey(self.pubk)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(content))
        return cipher_text

    def decrypt(self, ciphertext):
        if type(ciphertext) is str:
            ciphertext = ciphertext.encode('utf8')
        rsakey = crsa.importKey(self.privk)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        text = cipher.decrypt(
                base64.b64decode(ciphertext), self.random_generator)
        return text

    def sign(self, message):
        if type(message) is str:
            message = message.encode('utf8')
        rsakey = crsa.importKey(self.privk)
        signer = Signature_pkcs1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(message)
        sign = signer.sign(digest)
        sign = base64.b64encode(sign)
        return sign

    def verify(self, message, signature):
        if type(message) is str:
            message = message.encode('utf8')
        if type(signature) is str:
            signature = signature.encode('utf8')
        rsakey = crsa.importKey(self.pubk)
        verifier = Signature_pkcs1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(message)
        is_verify = verifier.verify(digest, base64.b64decode(signature))
        return is_verify


if __name__ == '__main__':
    privk = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAut/QQCcCvUfEAJRBr1od0hc5a8lY/W3Co3oT1acExNpzcvqe
j1Jv4+IlAn/T6btg0ZfAIqxCAScRH6LJl9QSmrStAkW7LVF7TQqi8fNqe8hTZA2t
nhH6H8ZVNCbkzhqwRIXOJ5TWfAebrdE2RJ1yh9E3G28JH8ovbses/YgWl8bUCMN6
gv7F7wFjhD1AvZG/J/efGrWFjssLVc+RWdGguByuIjIx7W2fw7JZziInC+IsR2Dw
U40hC5Zcih6IP6Zl0XqfB0II1SZDLwqU0VLXYRfMw+mwgRXSuxp+Hb8zQIxchCkB
TQmDPoNqGbS6BikhbSrVxkcXALhilhFO0PhLQQIDAQABAoIBAQCX4x/tdIeqdrEd
U2ML9i/0uYGnVPDqkxK3Mpr6dZTPt0pMsty7WuKskvtHy8Pe3rizwiadR+sh6rHl
R7eYmvtAGQfhp/GZxPd1x+Zmx1TOJSV6Vg++QZhNyTMpf09LIbAREbxcuYGXL8vd
/ASiwmH7eBXVS2tcFkZ1QQAe1USfuMwFFfqsMC9Qs6+1MtATUuctWcrMvT/Wcl8U
RSIWnSEQIYp6yXqpfthEEqKKWujOtd+B29P6dqfSRrge2F03BLO/1JJOfl2dxrZm
dbcXpvFiPqfBwqeT6PbsXCnGZOxhENNA/guhlraOMANWVlBF1vUSiRMRqW0kfB9N
37rqKOvNAoGBAOlOiEzDDQS/NJKro9zCFCn33L0Qy9WimRTHrnb1Yy9ycuguG2Y7
4qcrm6P7mnvOKlQuBRB28HLAqdlzN7VHzUMRjmFBMTctdKcQke0Bh6kFkSRSvtlV
8JDi8gD7685XTEMsWwMSf+yC/uNtiGZQevHq0377jQv39O03QvWleZK/AoGBAM0N
FhKq09vpzkjStF19JXU8jrTP2gHgKPV/5dWE4V1TeP/PoY+yIa2VMixntcvAI7Vc
3K4kfLg/BYyfLrO2ikfG9kfD15RJbr0WUxqP771vdMoSgcALVQjDIHUVkTFkH7NL
Mnf5tnib7hiw3Y8TwtjOk+L6ja4YvzYEmQH+q6H/AoGAbovcf2rIZ2Bl+71CVl7L
iRs9x4QG4UI7AKKg4xLgnWHAWo1GREnJ2mYKSEf2agVE/0AS/DsvMWBi2nsCgW31
L3tJGIH4XOm35VUvn7pi2k6d+DUQ4xAafbxa6OZ1U/7/TrDcqvcAEEP9nCuRPtGR
f8FB12A/89TYg/H0U0rF8ScCgYA8wgLnVxzdjcLlCyIMjZd6zI3Qf8IuShh43gPh
J7WLbL9utTw/Et4tzAaI59YTYIR0Kebt5rvZ8DqZt1UkRRNmP0scaqhHNRcOCj5n
oXy9Gfh2I9O0bucsaH0GlHRoOS23d7GloSVzSWjcghO0YHucuGFToUA39Pc7b1NT
Jv3+SwKBgAoPurAggGfWM7eLcj4PaeBfdE61bDRNTbjth8X1tryCtECvuY66NQ+8
h9EK5URYt9OufHMeowxqD4I4xFZ4QVBdXsUnSB8vYJwSksBso7KuNtqpmWRViU62
niu0fBDg9p9I9mMp2ELqbGmZl/Uyt7BA2lbepl6BQrqSzkIJ5mve
-----END RSA PRIVATE KEY-----"""
    pk = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAut/QQCcCvUfEAJRBr1od
0hc5a8lY/W3Co3oT1acExNpzcvqej1Jv4+IlAn/T6btg0ZfAIqxCAScRH6LJl9QS
mrStAkW7LVF7TQqi8fNqe8hTZA2tnhH6H8ZVNCbkzhqwRIXOJ5TWfAebrdE2RJ1y
h9E3G28JH8ovbses/YgWl8bUCMN6gv7F7wFjhD1AvZG/J/efGrWFjssLVc+RWdGg
uByuIjIx7W2fw7JZziInC+IsR2DwU40hC5Zcih6IP6Zl0XqfB0II1SZDLwqU0VLX
YRfMw+mwgRXSuxp+Hb8zQIxchCkBTQmDPoNqGbS6BikhbSrVxkcXALhilhFO0PhL
QQIDAQAB
-----END PUBLIC KEY-----"""

    rsa = RSA(privk, pk)
    ct = rsa.encrypt('123123a')
    print(ct)
    print("Decrypt:", rsa.decrypt(ct))

    message = "HeHe哒。"
    st = rsa.sign(message)
    print(st)
    print("Sign verify:", rsa.verify(message, st))
