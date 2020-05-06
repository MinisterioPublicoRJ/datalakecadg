from django.test import TestCase
from django.urls import reverse


class LandingPage(TestCase):
    def test_correct_response(self):
        url = reverse('core:home')
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'core/home.html')


class TestUploadManual(TestCase):
    def test_correct_upload(self):
        response = self.client.get(reverse("core:upload-manual"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/upload_manual.html")
