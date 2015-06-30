#!/usr/bin/python
# -*- coding: utf-8 -*-
""" utils functions
"""
__author__ = 'Zagfai'

import json
import datetime
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import smtplib
import os

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
        separators=(',', ':'), encoding='utf8')

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

def send(host, mail_from, mail_to_l, subject, text,
         user=None, pwd=None, cc_to_l=None, files=()):
    try:
        assert isinstance(files, (list,tuple)), 'File objs must be in list'
        assert isinstance(mail_from, str), 'Sender should be str'
        assert isinstance(subject, str), 'subject should be str'
        assert isinstance(text, str), 'subject should be str'
        assert isinstance(mail_to_l, (list,tuple)), 'Recevers must be in list'
        if cc_to_l is not None:
            assert isinstance(cc_to_l, (list,tuple)), 'CC must be in list'
        msg = MIMEMultipart()
        msg['From'] = mail_from
        msg['Subject'] = subject
        msg['To'] = ','.join(mail_to_l)  # COMMASPACE==', ' 
        if cc_to_l is not None:
            msg['CC'] = ','.join(cc_to_l)
        msg['Date'] = formatdate(localtime=True)
        msg.attach(MIMEText(text, _subtype='html', _charset='utf-8'))

        for _file in files:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(_file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(_file))
            msg.attach(part)

        smtp = smtplib.SMTP(host)
        if user and pwd:
            smtp.login(user, pwd)
        sendto = mail_to_l
        if cc_to_l is not None:
            sendto.extend(cc_to_l)
        smtp.sendmail(mail_from, sendto, msg.as_string())
        smtp.quit()
        # smtp.close()
        return True, 'sent'
    except Exception, e:
        return False, str(e)


if __name__ == '__main__':
    from hashlib import md5, sha1
    print bighash.md5(open('/home/zagfai/Desktop/try.c.out')).hexdigest()
    print md5(open('/home/zagfai/Desktop/try.c.out').read()).hexdigest()
    print bighash.sha1(open('/home/zagfai/Desktop/try.c.out')).hexdigest()
    print sha1(open('/home/zagfai/Desktop/try.c.out').read()).hexdigest()
    print bighash.md5('hello, crypto').hexdigest()
    print md5('hello, crypto').hexdigest()

