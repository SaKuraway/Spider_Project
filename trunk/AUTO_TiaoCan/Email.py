# -*-coding:utf-8-*-

import smtplib, time
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 不带SSL安全套层
from_addr = 'sakurapan@trussan.com'  # input('From: ')
password = 'Cbc_123'  # input('Password: ')
to_addr = [
    'sakurapan@trussan.com', 'yuwinliang@trussan.com', 'sarahguo@trussan.com', 'zainxue@trussan.com',
    '544538297@qq.com', 'iqpmw@126.com']  # input('To: ')
# to_addr = ['sakurapan@trussan.com','544538297@qq.com']     # input('To: ')
smtp_server = 'smtp.exmail.qq.com'  # input('SMTP server: ')
server = smtplib.SMTP(smtp_server, 25)

# SMTP服务器：smtp.exmail.qq.com(使用SSL，端口号465)
# smtp_server = 'smtp.exmail.qq.com'
# smtp_port = 465
# server = smtplib.SMTP(smtp_server, smtp_port)
# server.connect(smtp_server, smtp_port)
# server.starttls()

# 邮件对象:
msg = MIMEMultipart()
# msg = MIMEText('hello，收到请回复~', 'plain', 'utf-8')
msg['From'] = _format_addr('SaKura_AutoEmail<%s>' % from_addr)
msg['To'] = _format_addr('资管部人员<%s>' % to_addr)
msg['Subject'] = Header('Trussan自动调仓情况反馈', 'utf-8').encode()

# 邮件正文是MIMEText:
msg.attach(MIMEText(
            '今日调仓情况：今日战绩：调仓成功 6个 / 失败 0个。（附件为调仓总表）',
            'plain', 'utf-8'))

# 添加附件就是加上一个MIMEBase，从本地读取一个图片:
with open('Excel/ClientSwitch 201712.xls', 'rb') as f:
    # 设置附件的MIME和文件名，这里是png类型:
    mime = MIMEBase('excel', 'xls',
                    filename='ClientSwitch ' + time.strftime('%Y%m%d', time.localtime(
                        time.time())) + ' adjustment_situation.xls')
    # 加上必要的头信息:
    mime.add_header('Content-Disposition', 'attachment', filename='ClientSwitch ' + time.strftime('%Y%m%d', time.localtime(
                                time.time())) + ' adjustment_situation.xls')
    mime.add_header('Content-ID', '<0>')
    mime.add_header('X-Attachment-Id', '0')
    # 把附件的内容读进来:
    mime.set_payload(f.read())
    # 用Base64编码:
    encoders.encode_base64(mime)
    # 添加到MIMEMultipart:
    msg.attach(mime)

# 查看网络交互信息
server.set_debuglevel(1)
# 登录账户
server.login(from_addr, password)
# 发送邮件
server.sendmail(from_addr, to_addr, msg.as_string())
# 退出
server.quit()
