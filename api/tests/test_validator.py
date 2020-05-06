from unittest import TestCase, mock

from django.core.files.uploadedfile import SimpleUploadedFile

from api.forms import FileUploadForm


class TestValidator(TestCase):
    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_happy_path(self, _md5reader, _is_data_valid):
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

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_invalid_sent_md5(self, _md5reader, _is_data_valid):
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
        self.assertEqual(form.md5_, "md5 sum")
        self.assertEqual(form.errors["sent_md5"], ["valor md5 não confere!"])

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_file_extension(self, _md5reader, _is_data_valid):
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

    @mock.patch("api.forms.is_data_valid")
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_data_schema(self, _md5reader, _is_data_valid):
        _is_data_valid.return_value = (False, {"error": "error-msg"})
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
        self.assertEqual(
            form.errors["schema"],
            ["arquivo apresentou estrutura de dados inválida"]
        )

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_create_base_return(self, _md5reader, _is_data_valid):
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
        base_return = form.base_return

        self.assertFalse(is_valid)
        self.assertEqual(
            base_return,
            {
                "error": {"sent_md5": ["valor md5 não confere!"]},
                "md5": 'md5 sum'
            }
        )

    @mock.patch.object(FileUploadForm, "is_valid")
    def test_create_status_code(self, _is_valid):
        form_400_schema = FileUploadForm(data=dict(), files="file")
        form_400_schema._errors = [{"schema": "schema invalido"}]
        form_415 = FileUploadForm(data=dict(), files="file")
        form_415._errors = [{"filename": "arquivo deve ser gzip"}]
        form_400_md5 = FileUploadForm(data=dict(), files="file")
        form_400_md5._errors = [{"sent_md5": "md5 não confere"}]
        form_200 = FileUploadForm(data=dict(), files="file")
        form_200._errors = []

        self.assertEqual(form_400_schema.status_code, 400)
        self.assertEqual(form_400_md5.status_code, 400)
        self.assertEqual(form_415.status_code, 415)
        self.assertEqual(form_200.status_code, 200)
