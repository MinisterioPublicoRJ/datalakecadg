from unittest import TestCase, mock

from django.core.files.uploadedfile import SimpleUploadedFile

from api.forms import FileUploadForm


class TestValidator(TestCase):
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_happy_path(self, _md5reader):
        filename = "FILENAME.gz"
        data = {
            "username": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "sent_md5": "MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.errors, {})

    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_invalid_sent_md5(self, _md5reader):
        filename = "FILENAME.gz"
        data = {
            "username": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "sent_md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.errors["sent_md5"], ["valor md5 não confere!"])

    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_file_extension(self, _md5reader):
        filename = "FILENAME"
        data = {
            "username": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "sent_md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.errors["filename"], ["arquivo deve ser GZIP!"])
