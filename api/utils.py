from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from functools import wraps
from hashlib import md5


def securedecorator(func):

    @wraps(func)
    @require_http_methods(["POST"])
    def wrapper(*args, **kwargs):
        request = args[0]

        if 'SECRET' in request.POST and request.POST.get('SECRET') == settings.SECRET:
            return func(*args, **kwargs)

        raise PermissionDenied

    return wrapper


def md5reader(uploadedfile):
    hash_md5 = md5()
    for chunk in uploadedfile.chunks():
        hash_md5.update(chunk)

    uploadedfile.seek(0)
    return hash_md5.hexdigest()
