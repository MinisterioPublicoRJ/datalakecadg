from django.http import JsonResponse
from django.shortcuts import render
from os import path
from .clients import hdfsclient, methodmap
from .utils import md5reader



BASE_RETURN = {
    'md5': ''
}


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(
        path.join(destination, filename),
        file
    )


def upload(request):
    file = request.FILES['file']
    method = request.POST.get('method')
    filename = request.POST.get('filename')

    BASE_RETURN['md5'] = md5reader(file)

    if BASE_RETURN['md5'] != request.POST.get('md5'):
        return JsonResponse(BASE_RETURN, status=500)

    destination = methodmap[method]

    upload_to_hdfs(file.file, filename, destination)

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
