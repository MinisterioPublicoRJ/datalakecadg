from unittest import TestCase, mock

from django.core.files.uploadedfile import SimpleUploadedFile

from api.forms import FileUploadForm


class TestValidator(TestCase):
    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_happy_path(self, _md5reader, _is_data_valid):
        filename = "FILENAME.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.errors, {})

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_invalid_md5(self, _md5reader, _is_data_valid):
        filename = "FILENAME.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.md5_, "md5 sum")
        self.assertEqual(form.errors["md5"], ["valor md5 não confere!"])

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_file_extension(self, _md5reader, _is_data_valid):
        filename = "FILENAME"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
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
        filename = "FILENAME.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
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
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()
        base_return = form.base_return

        self.assertFalse(is_valid)
        self.assertEqual(
            base_return,
            {
                "error": {"md5": ["valor md5 não confere!"]},
                "md5": 'md5 sum'
            }
        )

    def test_form_stop_first_error(self):
        "Os dados possuem dois erros. A vaidação deve parar no primeiro error"
        filename = "FILENAME"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(len(form.errors), 1)

    @mock.patch("api.forms.md5reader")
    @mock.patch.object(FileUploadForm, "is_valid")
    def test_create_status_code(self, _is_valid, _md5reader):
        form_400_schema = FileUploadForm(data=dict(), files={"file": b"file"})
        form_400_schema._errors = {"schema": "schema invalido"}
        form_415 = FileUploadForm(data=dict(), files={"file": b"file"})
        form_415._errors = {"filename": "arquivo deve ser gzip"}
        form_400_md5 = FileUploadForm(data=dict(), files={"file": b"file"})
        form_400_md5._errors = {"md5": "md5 não confere"}
        form_201 = FileUploadForm(data=dict(), files={"file": b"file"})
        form_201._errors = []

        self.assertEqual(form_400_schema.status_code, 400)
        self.assertEqual(form_400_md5.status_code, 400)
        self.assertEqual(form_415.status_code, 415)
        self.assertEqual(form_201.status_code, 201)
