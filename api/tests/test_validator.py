from unittest import TestCase, mock

from api.forms import FileUploadForm
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy.mommy import make


class TestValidator(TestCase):
    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_happy_path(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".csv.gz",)
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.errors, {})

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_invalid_md5(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".csv.gz",)
        )
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(form.md5_, "md5 sum")
        self.assertEqual(form.errors["md5"], ["valor md5 não confere!"])

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_disable_md5_validation(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(
            data=data,
            files=file_to_send,
            disable_md5=True,
            good_exts=(".csv.gz",),
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_file_extension(self, _md5reader, _is_data_valid):
        filename = "FILENAME"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".ext", ".xyz")
        )
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["filename"], ["arquivo deve ser .ext, .xyz!"],
        )

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_also_accepts_pure_csv_files(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".csv",)
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.cleaned_data["filename"], "FILENAME.csv.gz")

    @mock.patch.object(FileUploadForm, "compress")
    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_gzip_file_if_pure_csv(self, _md5reader, _is_data_valid, _compress):
        filename = "FILENAME.csv"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_ = SimpleUploadedFile(filename, b"content")
        file_to_send = {"file": file_}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".csv",)
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.cleaned_data["filename"], "FILENAME.csv.gz")
        _compress.assert_called_once_with(file_)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_define_file_type(self, _md5reader, _is_data_valid):
        filename_csv = "FILENAME.csv"
        filename_gz = "FILENAME.csv.gz"
        data_csv = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename_csv,
            "md5": "MD5",
        }
        file_to_send_csv = {
            "file": SimpleUploadedFile(filename_csv, b"content")
        }
        data_gz = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename_gz,
            "md5": "MD5",
        }
        file_to_send_gz = {"file": SimpleUploadedFile(filename_gz, b"content")}
        form_csv = FileUploadForm(data=data_csv, files=file_to_send_csv)
        form_csv.is_valid()
        form_gz = FileUploadForm(data=data_gz, files=file_to_send_gz)
        form_gz.is_valid()

        self.assertTrue(form_csv.is_csv)
        self.assertFalse(form_gz.is_csv)

    @mock.patch("api.forms.is_data_valid")
    @mock.patch("api.forms.md5reader", return_value="MD5")
    def test_invalid_data_schema(self, _md5reader, _is_data_valid):
        _is_data_valid.return_value = (False, {"error": "error-msg"})
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "MD5",
        }
        file_ = SimpleUploadedFile(filename, b"content")
        file_to_send = {"file": file_}
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=(".csv.gz",)
        )
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["schema"],
            ["arquivo apresentou estrutura de dados inválida"],
        )
        self.assertEqual(form.errors["detail_schema"], {"error": "error-msg"})

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_create_base_return(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "filename": filename,
            "md5": "WRONG MD5",
        }
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        good_exts = (".csv.gz",)
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=good_exts
        )
        is_valid = form.is_valid()
        base_return = form.base_return

        self.assertFalse(is_valid)
        self.assertEqual(
            base_return,
            {"error": {"md5": ["valor md5 não confere!"]}, "md5": "md5 sum",},
        )

    def test_form_stop_first_error(self):
        "Os dados possuem dois erros. A validação deve parar no primeiro erro"
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

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_validate_original_filename_valid(self, _md5reader, _is_data_valid):
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "md5": "md5 sum",
        }
        filename = "FILENAME.csv.gz"
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        good_exts = (".csv.gz",)
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=good_exts
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.cleaned_data["filename"], filename)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_validate_original_filename_invalid(
        self, _md5reader, _is_data_valid
    ):
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "md5": "md5 sum",
        }
        filename = "FILENAME.csv.tsv"
        file_to_send = {"file": SimpleUploadedFile(filename, b"content")}
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_validate_given_filename_valid(self, _md5reader, _is_data_valid):
        filename = "FILENAME.csv.gz"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "md5": "md5 sum",
            "filename": filename,
        }
        file_to_send = {
            "file": SimpleUploadedFile("another_name.csv.gz", b"content")
        }
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        self.assertEqual(form.cleaned_data["filename"], filename)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_validate_given_filename_invalid(self, _md5reader, _is_data_valid):
        filename = "FILENAME.tsv"
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "md5": "md5 sum",
            "filename": filename,
        }
        file_to_send = {
            "file": SimpleUploadedFile("another_name.tsv", b"content")
        }
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)

    @mock.patch("api.forms.is_data_valid", return_value=(True, {}))
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_validate_given_filename_original_invalid(
        self, _md5reader, _is_data_valid
    ):
        filename = "FILENAME.csv"  # this one is valid
        data = {
            "nome": "USERNAME",
            "method": "METHOD-NAME",
            "md5": "md5 sum",
            "filename": filename,
        }
        # Original filename is invalid
        file_to_send = {
            "file": SimpleUploadedFile("another_name.tsv", b"content")
        }
        form = FileUploadForm(data=data, files=file_to_send)
        is_valid = form.is_valid()

        self.assertFalse(is_valid)

    @mock.patch("secret.models.login")
    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_convert_xslx_to_csv_before_validating(self, _md5reader, _login):
        username = "anyname"
        methodname = "cpf"

        secret = make("secret.Secret", username=username)
        mmap = make(
            "methodmapping.MethodMapping",
            method=methodname,
            uri="/path/to/storage/" + methodname,
            schema={
                "fields": [
                    {"name": "field1"},
                    {"name": "field2"},
                    {"name": "field3"},
                ]
            },
        )
        secret.methods.add(mmap)
        filename = "FILENAME.xlsx"
        data = {
            "nome": username,
            "method": methodname,
            "md5": "md5 sum",
            "filename": filename,
        }

        # Original filename is invalid
        with open("api/tests/assets/csv_example.xlsx", "rb") as file_:
            file_to_send = {"file": SimpleUploadedFile(filename, file_.read())}
        good_exts = (".xlsx",)
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=good_exts
        )
        is_valid = form.is_valid()

        self.assertTrue(is_valid)

    @mock.patch("api.forms.md5reader", return_value="md5 sum")
    def test_xlsx_file_cant_have_more_than_one_sheet(self, _md5reader):
        username = "anyname"
        methodname = "cpf"

        filename = "FILENAME.xlsx"
        data = {
            "nome": username,
            "method": methodname,
            "md5": "md5 sum",
            "filename": filename,
        }

        # Original filename is invalid
        with open("api/tests/assets/two_sheets.xlsx", "rb") as file_:
            file_to_send = {"file": SimpleUploadedFile(filename, file_.read())}

        good_exts = (".xlsx",)
        form = FileUploadForm(
            data=data, files=file_to_send, good_exts=good_exts
        )
        is_valid = form.is_valid()

        self.assertFalse(is_valid)
        self.assertEqual(
            form.errors["__all__"][0],
            "Os arquivos devem conter apenas uma aba. Verifique também as abas escondidas",
        )
