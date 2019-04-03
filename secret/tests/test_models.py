from unittest import mock

from django.test import TestCase

from model_mommy.mommy import make

from secret.models import Secret


class SendEmail(TestCase):
    @mock.patch('secret.models.send_mail')
    def test_send_email_when_associate_method_with_user(self, _send_mail):
        method = make('methodmapping.MethodMapping')
        secret = Secret(
            username='username',
            email='user@mail.com',
        )
        secret.save()
        secret.methods.add(method)
        secret.save()

        _send_mail.assert_called()
