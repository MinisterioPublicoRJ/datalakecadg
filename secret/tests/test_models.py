from django.core import mail
from django.test import TestCase

from model_mommy.mommy import make

from secret.models import Secret


class SendEmail(TestCase):
    def test_send_email_when_associate_method_with_user(self):
        method = make('methodmapping.MethodMapping')
        secret = Secret(
            username='username',
            email='user@mail.com',
        )
        secret.save()
        secret.methods.add(method)
        secret.save()

        self.assertEqual(len(mail.outbox), 1)
