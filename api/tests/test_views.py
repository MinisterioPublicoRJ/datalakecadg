import gzip

from hashlib import md5
from io import BytesIO
from unittest import mock

from django.urls import reverse
from django.test import TestCase
from model_mommy.mommy import make


class TestUpload(TestCase):
    @mock.patch('api.views.is_data_valid')
    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_file_post(self, _login, upload_to_hdfs, _send_mail,
                       _is_data_valid):
        _is_data_valid.return_value = (True, {})
        contents = b'filecontents'

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf'
        )
        secret.methods.add(mmap)

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': contents_md5,
                'method': 'cpf',
                'file': contents_file,
                'filename': 'filename.csv.gz'
            }
        )

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.json()['md5'], contents_md5)
        filename, dest = upload_to_hdfs.call_args[0][1:]
        self.assertEqual(filename, 'filename.csv.gz')
        self.assertEqual(dest, '/path/to/storage/cpf/' + secret.username)

    @mock.patch('api.views.is_data_valid')
    @mock.patch('api.views.upload_to_hdfs')
    def test_user_not_allowed_in_method(
            self, upload_to_hdfs, _is_data_valid):
        _is_data_valid.return_value = (True, {})
        contents = b'filecontents'

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        secret = make('secret.Secret', username='anyname')
        make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf'
        )

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': contents_md5,
                'method': 'cpf',
                'file': contents_file,
                'filename': 'filename.csv.gz'
            }
        )

        self.assertEqual(response.status_code, 403)

    @mock.patch('api.views.upload_to_hdfs')
    def test_file_post_wrong_md5(self, upload_to_hdfs):
        contents = b'filecontents'

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        secret = make('secret.Secret', username='anyname')

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': 'wrongmd5',
                'method': 'cpf',
                'file': contents_file,
                'filename': 'test.csv.gz'
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['md5'], contents_md5)
        self.assertEqual(response.json()['error'], 'md5 did not match')
        upload_to_hdfs.assert_not_called()

    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_validate_sent_data(self, _login, upload_to_hdfs, mm_added):
        with open('api/tests/csv_example.csv', 'rt', newline='') as file_:
            contents_md5 = md5(file_.read().encode()).hexdigest()
            file_.seek(0)

            secret = make('secret.Secret', username='anyname')
            mmap = make(
                'methodmapping.MethodMapping',
                method='cpf',
                uri='/path/to/storage/cpf'
            )
            secret.methods.add(mmap)
            response = self.client.post(
                reverse('api-upload'),
                {
                    'SECRET': secret.secret_key,
                    'nome': secret.username,
                    'md5': contents_md5,
                    'method': 'cpf',
                    'file': file_,
                    'filename': 'csv_example.csv'
                }
            )

            self.assertEqual(response.status_code, 415)
            self.assertEqual(
                response.json()['error'],
                'File must be a GZIP csv'
            )

    @mock.patch('api.views.is_data_valid')
    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_validate_sent_data_gzip(
            self,
            _login,
            upload_to_hdfs,
            mm_added,
            _is_data_valid
            ):
        _is_data_valid.return_value = (True, {})
        with gzip.open(
                'api/tests/csv_example_semicolon.csv.gz', 'rt', newline=''
        ) as file_:
            contents_md5 = md5(file_.read().encode()).hexdigest()
            file_.seek(0)

            secret = make('secret.Secret', username='anyname')
            mmap = make(
                'methodmapping.MethodMapping',
                method='cpf',
                uri='/path/to/storage/cpf',
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
                reverse('api-upload'),
                {
                    'SECRET': secret.secret_key,
                    'nome': secret.username,
                    'md5': contents_md5,
                    'method': 'cpf',
                    'file': file_,
                    'filename': 'csv_example_semicolon.csv.gz'
                }
            )

            self.assertEqual(response.status_code, 201)
            upload_to_hdfs.assert_called()

    @mock.patch("api.utils.read_csv_sample")
    @mock.patch("api.views.md5reader", return_value="md5 value")
    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_validated_schema_fail(
        self,
        _email_login,
        upload_to_hdfs,
        mm_added,
        _md5reader,
        _read_csv_sample,
    ):
        _read_csv_sample.return_value = [
            ['field1', 'field2', 'field3'], ["1", "2", "3"]
        ]
        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf',
            schema={
                "fields": [
                    {"name": "other_field1"},
                    {"name": "other_field2"},
                    {"name": "other_field3"},
                ]
            },
        )
        secret.methods.add(mmap)
        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': "md5 value",
                'method': 'cpf',
                'file': BytesIO(b"dummy content"),
                'filename': 'csv_example.csv.gz'
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertTrue(len(response.json()['error']))

    @mock.patch("api.utils.read_csv_sample")
    @mock.patch("api.views.md5reader", return_value="md5 value")
    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_validated_schema_success(
        self,
        _email_login,
        upload_to_hdfs,
        mm_added,
        _md5reader,
        _read_csv_sample,
    ):
        # Return different header
        _read_csv_sample.return_value = [
            ['field1', 'field2', 'field3'], ["1", "2", "3"]
        ]
        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf',
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
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': "md5 value",
                'method': 'cpf',
                'file': BytesIO(b"dummy content"),
                'filename': 'csv_example.csv.gz'
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('error', response.json())

    @mock.patch("api.utils.read_csv_sample")
    @mock.patch("api.views.md5reader", return_value="md5 value")
    @mock.patch('secret.models.send_mail')
    @mock.patch('api.views.upload_to_hdfs')
    @mock.patch('secret.models.login')
    def test_validated_schema_is_null_success(
        self,
        _email_login,
        upload_to_hdfs,
        mm_added,
        _md5reader,
        _read_csv_sample,
    ):
        _read_csv_sample.return_value = [
            ['field1', 'field2', 'field3'], ["1", "2", "3"]
        ]
        secret = make('secret.Secret', username='anyname')
        mmap = make(
            'methodmapping.MethodMapping',
            method='cpf',
            uri='/path/to/storage/cpf',
            schema=None,
        )
        secret.methods.add(mmap)
        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': "md5 value",
                'method': 'cpf',
                'file': BytesIO(b"dummy content"),
                'filename': 'csv_example.csv.gz'
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('error', response.json())
