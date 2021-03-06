import csv
import gzip
import logging
from functools import wraps
from hashlib import md5
from io import StringIO
from os import path

from api.clients import hdfsclient
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from goodtables import validate
from secret.models import Secret

logger = logging.getLogger(__name__)
FILE_ENCODING = "utf-8-sig"


class InvalidDelimiterException(Exception):
    pass


def securedecorator(func):
    @wraps(func)
    @require_http_methods(["POST"])
    def wrapper(*args, **kwargs):
        request = args[0]

        username = request.POST.get("nome", -1)
        secret = request.POST.get("SECRET", -1)
        if Secret.objects.filter(username=username, secret_key=secret):
            return func(*args, **kwargs)

        raise PermissionDenied

    return wrapper


def md5reader(uploadedfile):
    hash_md5 = md5()
    for chunk in uploadedfile.chunks():
        hash_md5.update(chunk)

    uploadedfile.file.seek(0)
    return hash_md5.hexdigest()


def read_csv_sample(file_, sample_size=100):
    if file_.name.endswith(".csv.gz"):
        fobj = gzip.open(file_, mode="rt", newline="", encoding=FILE_ENCODING)
    elif file_.name.endswith(".xlsx"):
        fobj = file_
    else:
        fobj = StringIO(file_.read().decode(FILE_ENCODING))
        fobj.seek(0)

    # delimiters must be ,
    dialect = csv.Sniffer().sniff(fobj.readline())
    if dialect.delimiter not in (",",):
        raise InvalidDelimiterException(
            "Arquivo contém delimitador inválido: '%s'" % dialect.delimiter
        )

    fobj.seek(0)
    reader = csv.reader(fobj, dialect)
    samples_count = 0
    sample_data = []
    for row in reader:
        sample_data.append(row)
        samples_count += 1
        if samples_count == sample_size:
            break

    fobj.seek(0)

    return sample_data


def is_data_valid(username, method, file_):
    dest = Secret.objects.filter(username=username, methods__method=method)
    if dest.exists():
        expected_schema = dest.first().methods.get(method=method).schema

        try:
            sample_data = read_csv_sample(
                file_, sample_size=settings.CSV_SAMPLE_SIZE,
            )
        except InvalidDelimiterException as error:
            logger.info("{0} | {1} - {2}".format(str(error), username, method))
            return False, str(error)

        validation = validate(sample_data, schema=expected_schema)
        if validation["valid"]:
            return True, {}
        else:
            return False, validation["tables"][0]["errors"]

    logger.info(
        "Erro ao encontrar método para usuário {0} - {1}".format(
            username, method
        )
    )
    return False, "Destino para upload não existe"


def get_destination(username, method):
    user_secret = Secret.objects.filter(
        username=username, methods__method=method
    )
    if user_secret.exists():
        return path.join(
            user_secret.get().methods.get(method=method).uri, username
        )

    raise PermissionDenied()


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(path.join(destination, filename), file, overwrite=True)
