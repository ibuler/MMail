#!/usr/bin/python
#coding: utf-8

import sys
import smtplib
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email.Header import Header

# 邮件主题
subject = open('mail_subject.txt').read().decode('utf-8')

## 设置SMTP服务器地址端口
smtpHost = 'smtp.qq.com'
smtpPort = 465
## 将来发送的邮件列表
toMails = []
## 打开文件读取邮件列表
f = open('mail_list.txt')
for mail in f:
    if mail and '@' in mail:
        toMails.append(mail)
f.close()

## 邮件内容读取
body = open('mail_content.html').read().decode('utf-8')

## 初始化邮件
encoding = 'utf-8'
##邮件内容转化为html格式
mail = MIMEText(body.encode(encoding), 'html', encoding)
mail['Subject'] = Header(subject, encoding)
mail['Date'] = formatdate() 

## 将文件中的发件人导入
auth = {}
f = open('mail_user.txt')
for line in f:
    if line:
        username = line.strip().split()[0]
        password = line.strip().split()[1]
        auth[username] = password
f.close()

# print auth

## 一层循环，为了保证所有邮件都被发送,当邮件列表为空时退出
while True:
    ## 二层循环，为了让发件人循环发送，每人发20封
    for username, password in auth.items(): 
        smtp = smtplib.SMTP_SSL(smtpHost, smtpPort)
        smtp.ehlo()
        try:
            print '#'*20, '%s' % username, '#'*20
            smtp.login(username, password)
        except smtplib.SMTPAuthenticationError:
            print 'Auth Error, exit!'
            sys.exit()
        total = len(toMails)

        ## 三层循环，为了发送邮件
        while True:
            try:
                toMail = toMails.pop().strip()
            except IndexError:
                break
            del mail['From']
            del mail['To']
            fromMail = username
            mail['From'] = fromMail
            mail['To'] = toMail
            try:
                smtp.sendmail(fromMail, toMail, mail.as_string())
                # print 'test send'
                # print mail.as_string()
            except (smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError):
                print 'send to %s Fail' % toMail
                continue
            else:
                print 'send to %s Ok' % toMail
            if len(toMails) < total - 20:
                total -= 20
                break
        smtp.close()

    if not len(toMails):
        break
