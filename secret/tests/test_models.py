from unittest import mock

from django.test import TestCase

from model_mommy.mommy import make

from secret.models import Secret


class SendEmail(TestCase):
    @mock.patch('secret.models.send_mail')
    @mock.patch('secret.models.login')
    def test_send_email_when_associate_method_with_user(self, _login,
                                                        _send_mail):
        method = make('methodmapping.MethodMapping')
        secret = Secret(
            username='username',
            email='user@mail.com',
        )
        secret.save()
        secret.methods.add(method)
        secret.save()

        _send_mail.assert_called()


class CreateSecret(TestCase):
    def test_dont_change_secret(self):
        "Test that user's secret is not changed everytime user object is saved"
        secret = Secret(
            username='username',
            email='user@mail.com'
        )
        secret.save()

        first_secret_key = secret.secret_key
        secret.save()

        self.assertEqual(secret.secret_key, first_secret_key)
