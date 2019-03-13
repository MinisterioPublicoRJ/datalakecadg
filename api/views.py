import logging

from os import path

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from .clients import hdfsclient
from .utils import md5reader, securedecorator

from methodmapping.models import MethodMapping

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
    dest = MethodMapping.objects.filter(
        secrets__username=username,
        method=method
    )
    if dest.exists():
        return path.join(dest.first().uri, username)


@securedecorator
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

    destination = get_destination(username, method)

    upload_to_hdfs(file.file, filename, destination)

    logger.info('%s successfully uploaded to HDFS' % filename)

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
