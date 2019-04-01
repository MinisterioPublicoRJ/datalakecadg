import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from secret.utils import create_secret


class Secret(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    secret_key = models.CharField(max_length=32, editable=False)
    methods = models.ManyToManyField('methodmapping.MethodMapping')

    def save(self, *args, **kwargs):
        self.secret_key = create_secret()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'User and Secret Key'
        verbose_name_plural = 'Users and Secret Keys'

    def __str__(self):
        return '{username} - {email}'.format(
            username=self.username, email=self.email
            )


@receiver(m2m_changed, sender=Secret.methods.through)
def methodmapping_added(sender, **kwargs):
    secret = kwargs.pop('instance', None)
    for method in secret.methods.all():
        method_description = method.description
        send_mail(
            'Adição de método',
            method_description,
            settings.EMAIL_HOST_USER,
            [secret.email]
        )
