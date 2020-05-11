from hashlib import md5
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from model_mommy.mommy import make

from api.utils import (
    securedecorator,
    md5reader,
    is_data_valid,
    get_destination,
    read_csv_sample,
)


@securedecorator
def postmethod(request):
    pass


class TestSecureDecorator(TestCase):
    def test_secure_empty_key(self):
        fakerequest = RequestFactory().post("")

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_empty_username(self):
        secret = make("secret.Secret", username="anyname")
        fakerequest = RequestFactory().post(
            "", data={"SECRET": secret.secret_key}
        )

        with self.assertRaises(PermissionDenied):
            postmethod(fakerequest)

    def test_secure_wrong_key(self):
        make(
            "secret.Secret", username="anyname",
        )
        fakerequest = RequestFactory().post(
            "", data={"nome": "anyname", "SECRET": "wrongkey"}
        )

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_secure_user_doesnt_match_secret(self):
        make(
            "secret.Secret", username="anyname",
        )
        fakerequest = RequestFactory().post(
            "", data={"nome": "othername", "SECRET": "aaaabbbcc"}
        )

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_secure(self):
        secret = make("secret.Secret", username="anyname",)
        fakerequest = RequestFactory().post(
            "", data={"nome": secret.username, "SECRET": secret.secret_key}
        )

        postmethod(request=fakerequest)


class TestMd5Reader(TestCase):
    def test_hexdigest(self):
        contents = b"filecontents"
        uploadedfile = SimpleUploadedFile("file", contents)

        self.assertEquals(md5reader(uploadedfile), md5(contents).hexdigest())

        self.assertEqual(uploadedfile.file.tell(), 0)

    def test_wronghexdigest(self):
        uploadedfile = SimpleUploadedFile("file", b"filecontents")

        self.assertNotEquals(
            md5reader(uploadedfile), md5(b"lerolero").hexdigest()
        )


class TestValidHeader(TestCase):
    @mock.patch("secret.models.login")
    def test_invalid_csd_NOT_comma_separated(self, _mail_login):
        gzipped_file = open("api/tests/csv_example_semicolon.csv.gz", "rb")
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

        valid, status = is_data_valid(secret.username, "cpf", gzipped_file)

        self.assertFalse(valid)
        self.assertTrue(len(status))

    @mock.patch("secret.models.login")
    def test_not_validate_header_if_schema_field_is_null(self, _mail_login):
        gzipped_file = open("api/tests/csv_example.csv.gz", "rb")
        secret = make("secret.Secret", username="anyname")
        mmap = make(
            "methodmapping.MethodMapping",
            method="cpf",
            uri="/path/to/storage/cpf",
            schema=None,
        )
        secret.methods.add(mmap)

        valid, status = is_data_valid(secret.username, "cpf", gzipped_file)

        self.assertTrue(valid)

    @mock.patch("secret.models.login")
    def test_validate_file_header_with_semicolon(self, _mail_login):
        gzipped_file = open("api/tests/csv_example.csv.gz", "rb")
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

        valid, status = is_data_valid(secret.username, "cpf", gzipped_file)

        self.assertTrue(valid)
        self.assertFalse(len(status))

    @mock.patch("secret.models.login")
    def test_invlid_destination(self, _mail_login):
        gzipped_file = open("api/tests/csv_example.csv.gz", "rb")
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

        valid, status = is_data_valid(
            "wrong-user", "wront-method", gzipped_file
        )

        self.assertFalse(valid)
        self.assertEqual(status, "Destino para upload não existe")


class TestMethodDestination(TestCase):
    @mock.patch("secret.models.login")
    def test_get_correct_destination(self, _mail_login):
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

        dest = get_destination(username, methodname)

        self.assertEqual(
            dest, "/path/to/storage/{0}/{1}".format(methodname, username)
        )

    @mock.patch("secret.models.login")
    def test_get_correct_destination_with_more_methods(self, _mail_login):
        username = "anyname"
        methodname_1 = "cpf"
        methodname_2 = "cnpj"

        secret = make("secret.Secret", username=username)
        mmap_1 = make(
            "methodmapping.MethodMapping",
            method=methodname_1,
            uri="/path/to/storage/" + methodname_1,
            schema={
                "fields": [
                    {"name": "field1"},
                    {"name": "field2"},
                    {"name": "field3"},
                ]
            },
        )
        mmap_2 = make(
            "methodmapping.MethodMapping",
            method=methodname_2,
            uri="/path/to/storage/" + methodname_2,
            schema={
                "fields": [
                    {"name": "field1"},
                    {"name": "field2"},
                    {"name": "field3"},
                ]
            },
        )
        secret.methods.add(mmap_1)
        secret.methods.add(mmap_2)

        dest = get_destination(username, methodname_2)

        self.assertEqual(
            dest, "/path/to/storage/{0}/{1}".format(methodname_2, username)
        )


class ReadCSVUtilsTest(TestCase):
    def test_read_gz_sample(self):
        with open("api/tests/csv_example.csv.gz", "rb") as gz_csv:
            sample_data = read_csv_sample(gz_csv)

        expected = [["field1", "field2", "field3"], ["1", "2", "3"]]

        self.assertEqual(sample_data, expected)

    def test_read_csv_sample(self):
        with open("api/tests/csv_example.csv", "rb") as gz_csv:
            sample_data = read_csv_sample(gz_csv)

        expected = [["field1", "field2", "field3"], ["1", "2", "3"]]

        self.assertEqual(sample_data, expected)
