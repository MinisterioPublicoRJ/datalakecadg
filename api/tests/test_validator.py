from unittest import TestCase

from django.core.files.uploadedfile import SimpleUploadedFile

from api.forms import FileUploadForm


class TestValidator(TestCase):
    def test_validate_file_extension(self):
        filename = "FILENAME.gz"
        data = {
            "username": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "sent_md5": "MD5"
        }
        file_to_send = {
            "file": SimpleUploadedFile(filename, b"content")
        }
        form = FileUploadForm(data=data, files=file_to_send)
        form.is_valid()

        self.assertEqual(form.errors, {})
