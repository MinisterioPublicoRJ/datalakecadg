import logging


from django.shortcuts import render

from api.forms import FileUploadForm
from api.utils import get_destination, upload_to_hdfs
from secret.models import Secret
logger = logging.getLogger(__name__)


def home(request):
    return render(request, "core/home.html")


def upload_manual(request):
    template_name = "core/upload_manual.html"
    if request.method == "GET":
        return render(request, template_name, {"form": FileUploadForm})
    else:
        # TODO: transformar validação abaixo em função
        username = request.POST.get("nome", -1)
        secret = request.POST.get("SECRET", -1)
        if Secret.objects.filter(
            username=username, secret_key=secret
        ).exists():
            form = FileUploadForm(
                data=request.POST, files=request.FILES, disable_md5=True
            )
            if form.is_valid():
                destination = get_destination(
                    form.cleaned_data["nome"], form.cleaned_data["method"]
                )
                upload_to_hdfs(
                    form.files["file"],
                    form.cleaned_data["filename"],
                    destination,
                )
                logger.info(
                    "username %s -> %s successfully uploaded to HDFS"
                    % (
                        form.cleaned_data["nome"],
                        form.cleaned_data["filename"],
                    )
                )
                return render(
                    request,
                    template_name,
                    {"form": form, "success": True}
                )
            else:
                return render(request, template_name, {"form": form})
        else:
            return render(
                request,
                template_name,
                {
                    "form": FileUploadForm,
                    "auth_error": "Chave secreta e/ou usuário incorretos",
                },
            )
