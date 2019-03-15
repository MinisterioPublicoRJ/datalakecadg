from django import forms
from django.core.exceptions import ValidationError

from secret.models import Secret


class SecretForm(forms.ModelForm):
    class Meta:
        model = Secret
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username']
        if Secret.objects.filter(username=username).exists():
            raise ValidationError("Usuário já existe!")
        return username
