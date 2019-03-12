from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect

from secret.forms import SecretForm


def create_secret(request):
    form = SecretForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Chave criada com sucesso!')

    context = {'form': form}
    return render(request, 'secret/create-secret.html', context)
