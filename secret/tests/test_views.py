from django.urls import reverse
from django.test import TestCase


class SecretView(TestCase):
    def test_correct_response(self):
        url = reverse('secret:create-secret')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
