from django.db import models

from secret.models import Secret


class MethodMapping(models.Model):
    method = models.CharField(max_length=255)
    uri = models.CharField(max_length=255)
    secrets = models.ManyToManyField(Secret)
