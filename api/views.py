import logging

from os import path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .clients import hdfsclient
from .utils import (
    md5reader,
    securedecorator,
    is_header_valid,
    get_destination)

logger = logging.getLogger(__name__)

BASE_RETURN = {
    'md5': ''
}


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(
        path.join(destination, filename),
        file,
        overwrite=True
    )


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
        logger.error(
            'username %s -> %s presented MD5 checksum error'
            % (filename, username)
        )
        BASE_RETURN['error'] = 'md5 did not match'
        BASE_RETURN['cgmd5'] = BASE_RETURN['md5'].encode().__repr__()
        BASE_RETURN['csmd5'] = sent_md5.encode().__repr__()
        return JsonResponse(BASE_RETURN, status=400)

    # Validate data file
    if not file.name.endswith('.gz') and not filename.endswith('.gz'):
        logger.error(
            'username: %s -> %s file is not a gzip'
            % (filename, username)
        )
        BASE_RETURN['error'] = 'File must be a GZIP csv'
        return JsonResponse(BASE_RETURN, status=415)

    # Validate file header
    valid_header, status = is_header_valid(username, method, file.file)
    if not valid_header:
        logger.error(
            'username: %s -> %s presented a non-valid header'
            % (filename, username)
        )
        BASE_RETURN['error'] = status
        return JsonResponse(BASE_RETURN, status=400)

    destination = get_destination(username, method)

    upload_to_hdfs(file.file, filename, destination)

    logger.info(
        'username %s -> %s successfully uploaded to HDFS'
        % (filename, username)
    )

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
