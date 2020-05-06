import csv
import gzip

from os import path

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from functools import wraps
from goodtables import validate
from hashlib import md5

from api.clients import hdfsclient
from secret.models import Secret


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
    with gzip.open(file_, "rt", newline="", encoding="utf-8-sig") as fobj:
        # force delimiter to be ','
        reader = csv.reader(fobj, delimiter=",")
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

        sample_data = read_csv_sample(
            file_, sample_size=settings.CSV_SAMPLE_SIZE,
        )
        validation = validate(sample_data, schema=expected_schema)
        if validation["valid"]:
            return True, {}
        else:
            return False, validation["tables"][0]["errors"]


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
