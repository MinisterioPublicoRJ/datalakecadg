from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect

from secret.forms import SecretForm
from secret.models import Secret


def create_secret(request):
    form = SecretForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        form.save()
        context['created_secret'] = Secret.objects.last().secret_key
        messages.success(request, 'Chave criada com sucesso!')

    return render(request, 'secret/create-secret.html', context)


def list_secret(request):
    context = {'secrets': Secret.objects.all()}
    return render(request, 'secret/list-secret.html', context)


def delete_secret(request, pk):
    secret = get_object_or_404(Secret, id=pk)
    if request.method == 'POST':
        secret.delete()
        return redirect('secret:list-secret')

    context = {'pk': pk, 'username': secret.username}
    return render(request, 'secret/delete-confirmation.html', context)
