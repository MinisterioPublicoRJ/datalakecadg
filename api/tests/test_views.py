from hashlib import md5
from io import BytesIO
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from model_mommy.mommy import make


class TestUpload(TestCase):
    @mock.patch("api.views.FileUploadForm")
    @mock.patch("api.views.upload_to_hdfs")
    def test_user_not_allowed_in_method(self, upload_to_hdfs, _FileForm):
        secret = make("secret.Secret", username="anyname")
        make(
            "methodmapping.MethodMapping",
            method="cpf",
            uri="/path/to/storage/cpf",
        )

        form_mock = mock.Mock()
        form_mock.is_valid.return_value = True
        form_mock.cleaned_data = {
            "nome": secret.username,
            "method": "cpf",
        }
        _FileForm.return_value = form_mock

        contents = b"filecontents"
        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        response = self.client.post(
            reverse("api-upload"),
            {
                "SECRET": secret.secret_key,
                "nome": secret.username,
                "md5": contents_md5,
                "method": "cpf",
                "file": contents_file,
                "filename": "filename.csv.gz",
            },
        )

        self.assertEqual(response.status_code, 403)

    @mock.patch("api.views.upload_to_hdfs")
    def test_file_post_wrong_md5(self, upload_to_hdfs):
        contents = b"filecontents"

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        secret = make("secret.Secret", username="anyname")

        response = self.client.post(
            reverse("api-upload"),
            {
                "SECRET": secret.secret_key,
                "nome": secret.username,
                "md5": "wrongmd5",
                "method": "cpf",
                "file": SimpleUploadedFile("test.csv.gz", b"filecontents"),
                "filename": "test.csv.gz",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["md5"], contents_md5)
        self.assertEqual(
            response.json()["error"]["md5"], ["valor md5 não confere!"]
        )
        upload_to_hdfs.assert_not_called()

    @mock.patch("secret.models.send_mail")
    @mock.patch("api.views.upload_to_hdfs")
    @mock.patch("secret.models.login")
    def test_validate_sent_data(self, _login, upload_to_hdfs, mm_added):
        with open("api/tests/csv_example.csv", "rt", newline="") as file_:
            contents_md5 = md5(file_.read().encode()).hexdigest()
            file_.seek(0)

            secret = make("secret.Secret", username="anyname")
            mmap = make(
                "methodmapping.MethodMapping",
                method="cpf",
                uri="/path/to/storage/cpf",
            )
            secret.methods.add(mmap)
            response = self.client.post(
                reverse("api-upload"),
                {
                    "SECRET": secret.secret_key,
                    "nome": secret.username,
                    "md5": contents_md5,
                    "method": "cpf",
                    "file": file_,
                    "filename": "csv_example.csv",
                },
            )

            self.assertEqual(response.status_code, 415)
            self.assertEqual(
                response.json()["error"]["filename"],
                ["arquivo deve ser GZIP!"],
            )

    @mock.patch("secret.models.send_mail")
    @mock.patch("api.views.upload_to_hdfs")
    @mock.patch("secret.models.login")
    def test_validate_sent_data_gzip(
        self, _login, upload_to_hdfs, mm_added,
    ):
        with open("api/tests/csv_example.csv.gz", "rb") as file_:
            contents_md5 = md5(file_.read()).hexdigest()
            file_.seek(0)

            secret = make("secret.Secret", username="anyname")
            mmap = make(
                "methodmapping.MethodMapping",
                method="cpf",
                uri="/path/to/storage/cpf",
                schema={
                    "fields": [
                        {"name": "field1"},
                        {"name": "field2"},
                        {"name": "field3"},
                    ]
                },
            )
            secret.methods.add(mmap)
            response = self.client.post(
                reverse("api-upload"),
                {
                    "SECRET": secret.secret_key,
                    "nome": secret.username,
                    "md5": contents_md5,
                    "method": "cpf",
                    "file": file_,
                    "filename": "csv_example_semicolon.csv.gz",
                },
            )

            self.assertEqual(response.status_code, 201)
            upload_to_hdfs.assert_called()

    @mock.patch("secret.models.send_mail")
    @mock.patch("api.views.upload_to_hdfs")
    @mock.patch("secret.models.login")
    def test_validated_schema_fail(
        self, _email_login, upload_to_hdfs, mm_added,
    ):
        secret = make("secret.Secret", username="anyname")
        mmap = make(
            "methodmapping.MethodMapping",
            method="cpf",
            uri="/path/to/storage/cpf",
            schema={
                "fields": [
                    {"name": "other_field1"},
                    {"name": "other_field2"},
                    {"name": "other_field3"},
                ]
            },
        )
        secret.methods.add(mmap)
        with open("api/tests/csv_example_semicolon.csv.gz", "rb") as file_:
            contents_md5 = md5(file_.read()).hexdigest()
            file_.seek(0)
            response = self.client.post(
                reverse("api-upload"),
                {
                    "SECRET": secret.secret_key,
                    "nome": secret.username,
                    "md5": contents_md5,
                    "method": "cpf",
                    "file": file_,
                    "filename": "csv_example.csv.gz",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(len(response.json()["error"]["schema"]))

    @mock.patch("secret.models.send_mail")
    @mock.patch("api.views.upload_to_hdfs")
    @mock.patch("secret.models.login")
    def test_validated_schema_success(
        self, _email_login, upload_to_hdfs, mm_added,
    ):
        # Return different header
        secret = make("secret.Secret", username="anyname")
        mmap = make(
            "methodmapping.MethodMapping",
            method="cpf",
            uri="/path/to/storage/cpf",
            schema={
                "fields": [
                    {"name": "field1"},
                    {"name": "field2"},
                    {"name": "field3"},
                ]
            },
        )
        secret.methods.add(mmap)
        with open("api/tests/csv_example.csv.gz", "rb") as file_:
            contents_md5 = md5(file_.read()).hexdigest()
            file_.seek(0)
            response = self.client.post(
                reverse("api-upload"),
                {
                    "SECRET": secret.secret_key,
                    "nome": secret.username,
                    "md5": contents_md5,
                    "method": "cpf",
                    "file": file_,
                    "filename": "csv_example.csv.gz",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["error"], {})

    @mock.patch("secret.models.send_mail")
    @mock.patch("api.views.upload_to_hdfs")
    @mock.patch("secret.models.login")
    def test_validated_schema_is_null_success(
        self, _email_login, upload_to_hdfs, mm_added,
    ):
        secret = make("secret.Secret", username="anyname")
        mmap = make(
            "methodmapping.MethodMapping",
            method="cpf",
            uri="/path/to/storage/cpf",
            schema=None,
        )
        secret.methods.add(mmap)
        with open("api/tests/csv_example_semicolon.csv.gz", "rb") as file_:
            contents_md5 = md5(file_.read()).hexdigest()
            file_.seek(0)
            response = self.client.post(
                reverse("api-upload"),
                {
                    "SECRET": secret.secret_key,
                    "nome": secret.username,
                    "md5": contents_md5,
                    "method": "cpf",
                    "file": file_,
                    "filename": "csv_example.csv.gz",
                },
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["error"], {})
