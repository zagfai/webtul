#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Info&Warn Module, use to send email, receive email, send sms,
and all other ways to send or receive info or warning messages.
working with aio
"""
__author__ = 'Zagfai'
__date__ = '2020-05'


import re
import traceback
import asyncio
import base64
import quopri
import aiosmtplib
import logging
from aioimaplib import aioimaplib
from email import message_from_bytes


class MailSystem(object):

    """Mail System to receive and send mail, work with gmail tested."""

    def __init__(self, loop, accounts):
        """Need a async loop to run this service

        :loop: async loop
        :accounts: [{name, addr, port, user, pwd}, ...]  # account list

        """
        self._loop = loop
        self._accounts = {i['mailname']: i for i in accounts}
        logging.info("Mail System initial finish...")

    async def receive_mail_loopy(self):
        await asyncio.sleep(3)
        while True:
            logging.info("Loop mail accounts.")
            for mailx in self._accounts:
                try:
                    await self._check_unread_mails(mailx)
                except Exception as e:
                    logging.info("Error mail loop %s %s" % (mailx, str(e)))
                    traceback.print_exc()
            await asyncio.sleep(60 * 15)

    async def _check_unread_mails(self, mailname):
        acc = self._accounts[mailname]
        imap_client = aioimaplib.IMAP4_SSL(*acc['imap'])
        await imap_client.wait_hello_from_server()
        await imap_client.login(acc['user'], acc['pwd'])

        await imap_client.select("INBOX")
        status, data = await imap_client.search('UNSEEN')
        if status != 'OK':
            await imap_client.logout()
            return
        mail_ids = data[0].split()
        logging.info('Mail %s UNSEEN size: %s' % (acc['user'], len(mail_ids)))
        for mailid in mail_ids[:8]:
            status, data = await imap_client.fetch(str(mailid), '(RFC822)')
            if status == 'OK':
                mail = message_from_bytes(data[1])
                from_mail = self.text_make(mail['From'])
                mail_addr = self._extra_mail_addr(from_mail)
                subject = self.text_make(mail['Subject'])
                body = self._get_body(mail)

                logging.info('Got mail %s from %s title "%s"' % (
                        mailid, from_mail, subject))

        await imap_client.logout()

    async def send(self, subject, body, mailname, to, text):
        host, port = self._accounts[mailname]['smtp']
        server = aiosmtplib.SMTP(
                host, port, loop=self._loop, timeout=10)
        await server.connect()
        await server.starttls()
        await server.login(self._accounts[mailname]['user'],
                           self._accounts[mailname]['pwd'])

        try:
            r = await server.sendmail(
                    self._accounts[mailname]['user'],
                    [to],
                    body.encode('utf8'))
            logging.info("Email sent: %s" % str(r))
        except Exception as e:
            logging.error("Email Error: %s" % str(e))
            return False

        await server.quit()
        return True

    def _get_body(self, mail):
        body = ""
        for part in mail.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(None, True)
                body = body.decode(errors='ignore')
                break
        return body

    def _extra_mail_addr(self, mail_from):
        regex = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"  # NOQA
        mails = re.findall(regex, mail_from)
        return mails[0]

    def text_make(self, words):
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
        reget = re.match(encoded_word_regex, words)
        if not reget:
            return words
        charset, encoding, encoded_text = reget.groups()
        if encoding == 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding == 'Q':
            byte_string = quopri.decodestring(encoded_text)
        return re.sub(encoded_word_regex, byte_string.decode(charset), words)


if __name__ == "__main__":
    logging.basicConfig(
            format='%(asctime)s [%(levelname)s] %(message)s',
            level=logging.INFO)
    LOOP = asyncio.get_event_loop()
    ACCOUNTS = [{
        "mailname": "Acer",
        "user": "test@gmail.com",
        "pwd": "33glglglglglgl",
        "smtp": ('smtp.gmail.com', 587),
        "imap": ("imap.gmail.com", 993),
    }]

    mail = MailSystem(LOOP, ACCOUNTS)
    LOOP.run_until_complete(mail.receive_mail_loopy())
    # LOOP.run_until_complete(mail.send('zagfai@test.net', "Memeda"))
    # str(email.header.make_header(email.header.decode_header(email_message['From'])))
    # str(email.header.make_header(email.header.decode_header(email_message['To'])))
    # str(email.header.make_header(email.header.decode_header(email_message['Subject'])))
