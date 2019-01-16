import logging
from django.http import JsonResponse
from django.shortcuts import render
from os import path
from .clients import hdfsclient, methodmap
from .utils import md5reader, securedecorator


logger = logging.getLogger(__name__)

BASE_RETURN = {
    'md5': ''
}


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(
        path.join(destination, filename),
        file
    )


@securedecorator
def upload(request):
    file = request.FILES['file']
    method = request.POST.get('method')
    filename = request.POST.get('filename')
    sent_md5 = request.POST.get('md5')

    BASE_RETURN['md5'] = md5reader(file)

    if BASE_RETURN['md5'] != sent_md5:
        logger.error('%s presented MD5 checksum error' % filename)
        return JsonResponse(BASE_RETURN, status=500)

    destination = methodmap[method]

    upload_to_hdfs(file.file, filename, destination)

    logger.info('%s successfully uploaded to HDFS' % filename)

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
