from django.contrib import admin

from secret.models import Secret


class SecretAdmin(admin.ModelAdmin):
    readonly_fields = ['secret_key']
    list_display = ('username', 'email', 'secret_key')


admin.site.register(Secret, SecretAdmin)
