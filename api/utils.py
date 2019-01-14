from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from functools import wraps


def securedecorator(func):

    @wraps(func)
    @require_http_methods(["POST"])
    def wrapper(*args, **kwargs):
        request = args[0]
        
        if 'SECRET' in request.POST and request.POST.get('SECRET') == settings.SECRET:
            return func(*args, **kwargs)

        raise PermissionDenied

    return wrapper
