from django.http import JsonResponse
from django.shortcuts import render
from .clients import hdfsclient
from .utils import md5reader


BASE_RETURN = {
    'md5': ''
}


def upload(request):
    file = request.FILES['file']
    BASE_RETURN['md5'] = md5reader(file)

    if BASE_RETURN['md5'] != request.POST.get('md5'):
        return JsonResponse(BASE_RETURN, status=500)

    return JsonResponse(
        BASE_RETURN,
        status=201
    )
