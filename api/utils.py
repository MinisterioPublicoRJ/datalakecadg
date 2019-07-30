import csv
import gzip

from os import path

from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from functools import wraps
from hashlib import md5

from secret.models import Secret


def securedecorator(func):

    @wraps(func)
    @require_http_methods(["POST"])
    def wrapper(*args, **kwargs):
        request = args[0]

        username = request.POST.get('nome', -1)
        secret = request.POST.get('SECRET', -1)
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


def is_header_valid(username, method, file_):
    dest = Secret.objects.filter(
        username=username,
        methods__method=method
    )
    if dest.exists():
        expected_headers = dest.first().methods.first().mandatory_headers
        # If expected_headers is empty do not need to make validation
        if expected_headers == '':
            return True, {}

        with gzip.open(file_, 'rt', newline='', encoding='utf-8-sig') as fobj:
            dialect = csv.Sniffer().sniff(fobj.readline())
            fobj.seek(0)
            reader = csv.reader(fobj, dialect)
            header = next(reader)
            file_.seek(0)
            if header == expected_headers.split(','):
                return True, {}
            else:
                return (False,
                        'File must contain the following headers: {0}.'
                        ' Received: {1}'.format(
                            expected_headers,
                            ','.join(header)
                        ))


def get_destination(username, method):
    user_secret = Secret.objects.filter(
        username=username,
        methods__method=method
    )
    if user_secret.exists():
        return path.join(
            user_secret.get().methods.get(method=method).uri,
            username
        )

    raise PermissionDenied()
