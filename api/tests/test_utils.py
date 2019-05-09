from hashlib import md5
from unittest import mock

from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from model_mommy.mommy import make

from api.utils import (
    securedecorator,
    md5reader,
    is_header_valid,
    get_destination)


@securedecorator
def postmethod(request):
    pass


class TestSecureDecorator(TestCase):
    def test_secure_empty_key(self):
        fakerequest = RequestFactory().post('')

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_empty_username(self):
        secret = make('secret.Secret', username='anyname')
        fakerequest = RequestFactory().post(
            '',
            data={'SECRET': secret.secret_key}
        )

        with self.assertRaises(PermissionDenied):
            postmethod(fakerequest)

    def test_secure_wrong_key(self):
        make(
            'secret.Secret',
            username='anyname',
        )
        fakerequest = RequestFactory().post(
            '',
            data={
                'nome': 'anyname',
                'SECRET': 'wrongkey'
            }
        )

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_secure_user_doesnt_match_secret(self):
        make(
            'secret.Secret',
            username='anyname',
        )
        fakerequest = RequestFactory().post(
            '',
            data={
                'nome': 'othername',
                'SECRET': 'aaaabbbcc'
            }
        )

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_secure(self):
        secret = make(
            'secret.Secret',
            username='anyname',
        )
        fakerequest = RequestFactory().post(
            '',
            data={'nome': secret.username, 'SECRET': secret.secret_key}
        )

        postmethod(request=fakerequest)


class TestMd5Reader(TestCase):
    def test_hexdigest(self):
        contents = b'filecontents'
        uploadedfile = SimpleUploadedFile(
            'file',
            contents
        )

        self.assertEquals(
            md5reader(uploadedfile),
            md5(contents).hexdigest()
        )

        self.assertEqual(uploadedfile.file.tell(), 0)

    def test_wronghexdigest(self):
        uploadedfile = SimpleUploadedFile(
            'file',
            b'filecontents'
        )

        self.assertNotEquals(
            md5reader(uploadedfile),
            md5(b'lerolero').hexdigest()
        )


class TestValidHeader(TestCase):
    @mock.patch('secret.models.send_mail')
    def test_validate_file_header(self, _send_mail):
        gzipped_file = open('api/tests/csv_example.csv.gz', 'rb')
        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf',
            mandatory_headers='field1,field2,field3'
        )
        secret.methods.add(mmap)

        valid, status = is_header_valid(secret.username, 'cpf', gzipped_file)

        self.assertTrue(valid)

    @mock.patch('secret.models.send_mail')
    def test_not_validate_header_if_mandatory_field_is_empty(self, _send_mail):
        gzipped_file = open('api/tests/csv_example.csv.gz', 'rb')
        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf',
            mandatory_headers=''
        )
        secret.methods.add(mmap)

        valid, status = is_header_valid(secret.username, 'cpf', gzipped_file)

        self.assertTrue(valid)


class TestMethodDestination(TestCase):
    @mock.patch('secret.models.send_mail')
    def test_get_correct_destination(self, _send_mail):
        username = 'anyname'
        methodname = 'cpf'

        secret = make('secret.Secret', username=username)
        mmap = make(
            'methodmapping.MethodMapping',
            method=methodname,
            uri='/path/to/storage/cpf',
            mandatory_headers='field1,field2,field3'
        )
        secret.methods.add(mmap)

        dest = get_destination(username, methodname)

        self.assertEqual(
            dest,
            '/path/to/storage/{0}/{1}'.format(methodname, username)
        )

    @mock.patch('secret.models.send_mail')
    def test_get_correct_destination_with_more_methods(self, _send_mail):
        username = 'anyname'
        methodname_1 = 'cpf'
        methodname_2 = 'cnpj'

        secret = make('secret.Secret', username=username)
        mmap_1 = make(
            'methodmapping.MethodMapping',
            method=methodname_1,
            uri='/path/to/storage/' + methodname_1,
            mandatory_headers='field1,field2,field3'
        )
        mmap_2 = make(
            'methodmapping.MethodMapping',
            method=methodname_2,
            uri='/path/to/storage/' + methodname_2,
            mandatory_headers='field1,field2,field3'
        )
        secret.methods.add(mmap_1)
        secret.methods.add(mmap_2)

        dest = get_destination(username, methodname_2)

        self.assertEqual(
            dest,
            '/path/to/storage/{0}/{1}'.format(methodname_2, username)
        )
