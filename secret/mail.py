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


msg_template = """
<p>Olá {username}, você recebeu este e-mail pois foi autorizada a enviar dados
para o método {method} na API do Data Lake MP em Mapas.
Seguem abaixo informações sobre os dados esperados e instruções para a realização do envio.</p>
<br/>
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
  <li>'nome': (string) nome do usuário: '{username}'</li>
  <li>'md5': (string) hash MD5 hexadecimal de 32 posições do arquivo enviado, em minúsculas</li>
  <li>'method':(string) nome do método '{method}'</li>
  <li>'SECRET':(string) Chave hexadecimal '{secret}'</li>
</ul>

"""
