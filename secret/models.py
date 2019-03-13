import uuid

from django.db import models

from secret.utils import create_secret


class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    secret_key = models.CharField(max_length=32, editable=False)

    def save(self, *args, **kwargs):
        self.secret_key = create_secret()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User and Secret Key'
        verbose_name_plural = 'Users and Secret Keys'

    def __str__(self):
        return f'{self.username} - {self.email}'
