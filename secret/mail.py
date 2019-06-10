import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from decouple import config
from jinja2 import Template


def login():
    server = smtplib.SMTP(config('EMAIL_SMTP_SERVER'))
    return server


def send_mail(server, msg, dest):
    msg_mime = MIMEMultipart('alternative')
    msg_mime.set_charset('utf8')
    msg_mime['FROM'] = config('EMAIL_HOST_USER')
    msg_mime['Subject'] = config('EMAIL_SUBJECT')
    attach = MIMEText(msg.encode('utf-8'), 'html', 'UTF-8')
    msg_mime.attach(attach)
    server.sendmail(
        config('EMAIL_HOST_USER'),
        dest,
        msg_mime.as_string()
    )


with open('core/templates/core/email.html') as fobj:
    msg_template = Template(fobj.read())
