from django.http import HttpResponse
from django.shortcuts import render

from secret.forms import SecretForm


def create_secret(request):
    form = SecretForm(request.POST or None)
    if form.is_valid():
        form.save()
        return HttpResponse()

    context = {'form': form}
    return render(request, 'secret/create-secret.html', context)
