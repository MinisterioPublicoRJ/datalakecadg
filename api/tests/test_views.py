from hashlib import md5
from io import BytesIO
from unittest import mock

from django.urls import reverse
from django.test import TestCase
from model_mommy.mommy import make


class TestUpload(TestCase):
    @mock.patch('api.views.upload_to_hdfs')
    def test_file_post(self, upload_to_hdfs):
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
        mmap.secrets.add(secret)

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': secret.secret_key,
                'nome': secret.username,
                'md5': contents_md5,
                'method': 'cpf',
                'file': contents_file,
                'filename': 'filename'
            }
        )

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.json()['md5'], contents_md5)
        filename, dest = upload_to_hdfs.call_args[0][1:]
        self.assertEqual(filename, 'filename')
        self.assertEqual(dest, '/path/to/storage/cpf/' + secret.username)

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
                'file': contents_file
            }
        )

        self.assertEquals(response.status_code, 500)
        self.assertEquals(response.json()['md5'], contents_md5)
        upload_to_hdfs.assert_not_called()
