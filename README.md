##  MageMail v0.1
## 目的是批量发送邮件
mail_subject.txt     该文件中内容为邮件主题
mail_content.html    该文件中存放的是要发送邮件的内容，格式是html格式的，可以从qq邮箱里面格式-html中复制过来
mail_user.txt        该文件中存放发件人的账号密码，空格隔开，有循环用里面的用户发送邮件
mail_list.txt        该文件中存放的是收件人的地址，每个地址一行

## 使用方法
python qmail.py      屏幕会提示用哪个账号发送，并提示发送状态结果
