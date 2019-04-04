import uuid

from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from secret.utils import create_secret
from secret.mail import login, send_mail, msg_template


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
    dest = [secret.email]
    mail_server = login()
    for method in secret.methods.all():
        msg = msg_template.render(
            username=secret.username,
            description=method.description,
            method=method.method,
            secret=secret.secret_key,
            headers=method.mandatory_headers.split(',')
        )
        send_mail(mail_server, msg, dest)
