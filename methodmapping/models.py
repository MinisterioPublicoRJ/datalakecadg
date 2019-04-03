from django.db import models


class MethodMapping(models.Model):
    method = models.CharField(max_length=255)
    uri = models.CharField(
        max_length=255,
        help_text="Exemplo: /user/mpmapas/staging/labcontas/cpf"
    )
    description = models.TextField()
    mandatory_headers = models.TextField()

    def __str__(self):
        return '{method}: {uri}'.format(method=self.method, uri=self.uri)
