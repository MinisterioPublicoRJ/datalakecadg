import logging

from os import path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from api.forms import FileUploadForm
from .clients import hdfsclient
from .utils import securedecorator, get_destination

logger = logging.getLogger(__name__)


def upload_to_hdfs(file, filename, destination):
    hdfsclient.write(path.join(destination, filename), file, overwrite=True)


@securedecorator
@csrf_exempt
def upload(request):
    form = FileUploadForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        destination = get_destination(
            form.cleaned_data["nome"], form.cleaned_data["method"]
        )
        upload_to_hdfs(
            form.files["file"], form.cleaned_data["filename"], destination
        )
        logger.info(
            "username %s -> %s successfully uploaded to HDFS"
            % (form.cleaned_data["nome"], form.cleaned_data["filename"])
        )

    return JsonResponse(form.base_return, status=form.status_code)
