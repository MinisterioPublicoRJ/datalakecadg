import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from decouple import config


def login():
    server = smtplib.SMTP(config('EMAIL_SMTP_SERVER'))
    return server


def send_mail(server, msg, dest):
    msg_mime = MIMEMultipart('alternative')
    msg_mime.set_charset('utf8')
    msg_mime['FROM'] = config('EMAIL_HOST_USER')
    msg_mime['Subject'] = config('EMAIL_SUBJECT')
    msg_mime['To']
    attach = MIMEText(msg.encode('utf-8'), 'html', 'UTF-8')
    msg_mime.attach(attach)
    server.sendmail(
        config('EMAIL_HOST_USER'),
        dest,
        msg_mime.as_string()
    )


msg_template = """Olá {username}, seguem abaixo informações sobre os dados e
como enviá-los.
</br></br>

<strong>Descrição dos Dados:</strong>

{description}
<br/><br/>

<strong>Protocolo/Método:</strong>
  HTTP - POST

<br/>

<strong>Enctype:</strong>
  multipart/form-data
<br/>
<strong>Data:</strong>
<ul>
  <li>'filename': (string) nome completo do arquivo, ex.: placas_20190110.csv.gz</li>
  <li>'nome': (string) 'detranbarreirasplacas'</li>
  <li>'md5': (string) hash MD5 hexadecimal de 32 posições, em minúsculas</li>
  <li>'method': 'detranbarreirasplacas'</li>
  <li>'SECRET': "*****" (chave hexad)</li>
</ul>

"""
