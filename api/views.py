import logging

from os import path

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .clients import hdfsclient
from .utils import md5reader, securedecorator

from secret.models import Secret

logger = logging.getLogger(__name__)

BASE_RETURN = {
    'md5': ''
}


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(
        path.join(destination, filename),
        file
    )


def get_destination(username, method):
    dest = Secret.objects.filter(
        username=username,
        methods__method=method
    )
    if dest.exists():
        return path.join(dest.first().methods.first().uri, username)

    raise PermissionDenied()


@securedecorator
@csrf_exempt
def upload(request):
    file = request.FILES['file']
    username = request.POST.get('nome')
    method = request.POST.get('method')
    filename = request.POST.get('filename')
    sent_md5 = request.POST.get('md5')

    BASE_RETURN['md5'] = md5reader(file)

    if BASE_RETURN['md5'] != sent_md5:
        logger.error('%s presented MD5 checksum error' % filename)
        return JsonResponse(BASE_RETURN, status=500)

    # Validate data file
    if not file.name.endswith('.gz') and not filename.endswith('.gz'):
        logger.error('%s file is not a gzip' % filename)
        BASE_RETURN['error'] = 'File must be a GZIP csv'
        return JsonResponse(BASE_RETURN, status=400)

    destination = get_destination(username, method)

    upload_to_hdfs(file.file, filename, destination)

    logger.info('%s successfully uploaded to HDFS' % filename)

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
