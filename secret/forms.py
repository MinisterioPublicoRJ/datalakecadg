from django import forms

from secret.models import Secret


class SecretForm(forms.ModelForm):
    class Meta:
        model = Secret
        fields = ['username', 'email']
