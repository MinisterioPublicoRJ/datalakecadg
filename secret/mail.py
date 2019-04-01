import smtplib

from decouple import config


def login():
    server = smtplib.SMTP(config('EMAIL_SMTP_SERVER'))
    return server


def send_mail(server, msg, dest):
    server.sendmail(
        config('EMAIL_HOST_USER'),
        dest,
        msg
    )


msg_template = """Olá {username}, seguem abaixo informações sobre os dados e
como enviá-los.

{description}

Protocolo/Método:
  HTTP - POST

Enctype:
  multipart/form-data

Data:
  'filename': (string) nome completo do arquivo, ex.: placas_20190110.csv.gz
  'nome': (string) 'detranbarreirasplacas'
  'md5': (string) hash MD5 hexadecimal de 32 posições, em minúsculas
  'method': 'detranbarreirasplacas'
  'SECRET': "*****" (chave hexad)

"""
