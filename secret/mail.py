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
    msg_mime['To']
    attach = MIMEText(msg.encode('utf-8'), 'html', 'UTF-8')
    msg_mime.attach(attach)
    server.sendmail(
        config('EMAIL_HOST_USER'),
        dest,
        msg_mime.as_string()
    )


msg_template = Template("""
<p>Olá {{ username }}, você recebeu este e-mail pois foi autorizada a enviar dados<br/>
para o método {method} na API do Data Lake MP em Mapas.
Seguem abaixo informações sobre os dados esperados e instruções para a realização do envio.</p>
<br/>
<strong>Descrição dos Dados:</strong>

{{ description }}
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
  <li>'nome': (string) nome do usuário - '{{ username }}'</li>
  <li>'md5': (string) hash MD5 hexadecimal de 32 posições do arquivo enviado, em minúsculas</li>
  <li>'method':(string) nome do método - '{{ method }}'</li>
  <li>'SECRET':(string) Chave hexadecimal - '{{ secret }}'</li>
</ul>

<br/>
<strong>Files:</strong>
 <ul>
     <li>'file' (Bytes): Arquvio a ser enviado para a CADG</li>
     <li>'filename' (string): nome do arquivo idêntico ao informado no Data</li>
 </ul>

 <br/>

<strong>Formato do arquivo CSV (gzipped) esperado:</strong>
 <ul>
    <li>Charset: UTF-8</li>
    <li>Separator: ;</li>
    <li>Quote: ""</li>
    <li>Line terminator: \n</li>
 </ul>

<br/>

<strong>Compactação do Arquivo CSV:</strong>
<ul>
    <li>gzip</li>
</ul>

<br/>

<strong>Formato do nome do Arquivo:</strong>
<ul>
<li>Nome (formato:[a-z0-9]+).csv.gz ex.: placas_20190110.csv.gz</li>
</ul>

<br/>

<strong>Campos esperados:</strong>
<ul>
{% for header in headers %}
    <li>{{ header }}</li>
{% endfor %}
</ul>

<br/>

<strong>Resposta:</strong>
<ul>
    <li>OK: status_code: 201 - Arquivo salvo com sucesso</li>
    <li>Não OK: status code: 403 - SECRET, username e/ou method estão errados</li>
    <li>Não OK: status code: 415 - md5 enviado não é o mesmo que o calculado em nosso serviço</li>
    <li>Não OK: status code: 400 - Extensão do arquivo enviado inválida ou cabeçalhos do arquivo csv inválidos</li>
</ul>
<br/>

<strong>Importante</strong>
<p>Os arquivos são registrados no Big Data por seus nomes.
Normalize o nome do arquivo de acordo com seu lote e índice, para que arquivos
anteriores
não sejam sobrescritos.
Arquivos novos sobrescreverão arquivos homônimos no BDA.</p>

""")
