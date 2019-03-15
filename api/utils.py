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
