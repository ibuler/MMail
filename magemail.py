#!/usr/bin/python
#coding: utf-8

import sys
import time
import smtplib
import ConfigParser
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header

config = 'magemail.conf'
encoding = 'utf-8'


class MageMail(object):
    """ Mage Mail class """
    def __init__(self):
        cf = ConfigParser.ConfigParser()
        cf.read(config)
        self.smtphost = cf.get('global', 'smtp')
        self.smtpport = cf.get('global', 'port')
        self.every_send_nums = int(cf.get('global', 'every_send_nums'))
        self.send_per_sleep = float(cf.get('global', 'send_per_sleep'))
        self.every_account_send_sleep = float(cf.get('global', 'every_account_send_sleep'))
        self.all_account_sleep = float(cf.get('global', 'all_account_sleep'))
        self.mail_user_file = cf.get('global', 'mail_user')
        self.mail_list_file = cf.get('global', 'mail_list')
        self.mail_content_file = cf.get('global', 'mail_content')
        self.mail_subject_file = cf.get('global', 'mail_subject')
        self.subject = self._read_to_utf8(self.mail_subject_file)
        self.body = self._read_to_utf8(self.mail_content_file)
        self.mail = MIMEText(self.body.encode(encoding), 'html', encoding)
        self.to_mails = self._read_mail_list(self.mail_list_file)

    def _read_to_utf8(self, filename):
        """Read content from a file, and encoding to utf-8"""
        f = open(filename, 'r')
        content = f.read().decode('utf-8')
        f.close()
        return content

    def _read_mail_list(self, filename):
        """read mail_list from a file , to a list"""
        to_mails = []
        f = open(filename)
        for line in f:
            if '@' in line:
                to_mails.append(line)
        f.close()
        return to_mails

    def _read_mail_user(self, file):
        """read mail user from a file to a dict object"""
        auth = {}
        f = open(file)
        for line in f:
            if line:
                try:
                    username, password = line.strip().split()
                except ValueError:
                    print 'mail_user file format error.'
                    return
                auth[username] = password
        f.close()
        return auth

    def _init_mail(self, from_addr=None, to_addr=None):
        """init a mail object"""
        self.mail['Subject'] = Header(self.subject, encoding)
        self.mail['Date'] = formatdate()
        self.mail['From'] = from_addr
        self.mail['To'] = to_addr

    def _send_mail(self, username, password, mail_addr, mail):
        """send a mail"""
        smtp = smtplib.SMTP_SSL(self.smtphost, self.smtpport)
        smtp.ehlo()
        try:
            smtp.login(username, password)
        except smtplib.SMTPAuthenticationError:
            print '%s: %s Auth Error, exit!' % (username, password)
            return
        
        try:
            smtp.sendmail(username, mail_addr, mail.as_string())
            # print 'Test Sending!'
            # print mail.as_string()
        except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError):
            print 'send mail to %s Failed.' % mail_addr
        else:
            print 'send mail to %s Ok.' % mail_addr
        finally:
            smtp.close()

    def save_other(self, a_list, filename):
        """save not send mail_list to the mail_list file"""
        f = open(filename, 'w')
        for line in a_list:
            f.write('%s' % line)
        f.close()

    def run(self):
        auth = self._read_mail_user(self.mail_user_file)
        while True:
            for username, password in auth.items():
                print '#'*20, username, '#'*20
                for i in range(self.every_send_nums):
                    try:
                        to_mail = self.to_mails.pop().strip()
                    except IndexError:
                        print 'Mail_list is empty.'
                        sys.exit()
                    self._init_mail(username, ','.join(to_mail.split()))
                    self._send_mail(username, password, to_mail.split(), self.mail)
                    time.sleep(self.send_per_sleep)
                time.sleep(self.every_account_send_sleep)
            print 'Prepare SendMail Next Loop!'
            time.sleep(self.all_account_sleep)


if __name__ == '__main__':
    mail = MageMail()
    try:
        mail.run()
    except KeyboardInterrupt, e:
        mail.save_other(mail.to_mails, mail.mail_list_file)