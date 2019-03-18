from django.contrib import admin

from methodmapping.models import MethodMapping


class MethodMappingAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(MethodMappingAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['uri'].initial = '/user/mpmapas/staging/'
        return form


admin.site.register(MethodMapping, MethodMappingAdmin)
