from django import forms
from django.db.models.functions import Lower
from django.contrib import admin

from methodmapping.models import MethodMapping
from secret.models import Secret


class SecretAdminForm(forms.ModelForm):
    methods = forms.ModelMultipleChoiceField(
        queryset=MethodMapping.objects.all().order_by(Lower('uri'))
    )

    class Meta:
        model = MethodMapping
        fields = '__all__'


class SecretAdmin(admin.ModelAdmin):
    readonly_fields = ['secret_key']
    list_display = ('username', 'email', 'secret_key')
    form = SecretAdminForm


admin.site.register(Secret, SecretAdmin)
