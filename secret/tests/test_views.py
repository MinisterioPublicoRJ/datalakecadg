from django.contrib.messages import get_messages
from django.urls import reverse
from django.test import TestCase
from freezegun import freeze_time
from model_mommy.mommy import make

from secret.models import Secret


class SecretView(TestCase):
    def test_correct_response(self):
        url = reverse('secret:create-secret')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)

    @freeze_time('2019-03-12 12:00:00')
    def test_create_secret_key(self):
        url = reverse('secret:create-secret')
        data = {
            'username': 'anyname',
            'email': 'any@email.com'
        }
        resp = self.client.post(url, data=data)
        user = Secret.objects.last()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(user.username, 'anyname')
        self.assertEqual(user.email, 'any@email.com')
        self.assertEqual(user.secret_key, 'd3a4646728a9de9a74d8fc4c41966a42')

    def test_template_used(self):
        url = reverse('secret:create-secret')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'secret/create-secret.html')
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertIn('Chave criada com sucesso', messages)


class SecretList(TestCase):
    def test_correct_response(self):
        make(Secret, _quantity=2)
        url = reverse('secret:list-secret')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'secret/list-secret.html')
        self.assertEqual(resp.context['secrets'].count(), 2)
