from django.db import models

from secret.utils import create_secret


class Secret(models.Model):
    username = models.CharField(max_length=255)
    email = models.EmailField()
    secret_key = models.CharField(max_length=32)

    def save(self, *args, **kwargs):
        self.secret_key = create_secret()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} - {self.email}'
