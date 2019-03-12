from hashlib import md5
from io import BytesIO
from unittest import mock

from django.conf import settings
from django.urls import reverse
from django.test import TestCase


class TestUpload(TestCase):
    @mock.patch('api.views.upload_to_hdfs')
    def test_file_post(self, upload_to_hdfs):
        contents = b'filecontents'

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': settings.SECRET,
                'md5': contents_md5,
                'method': 'cpf',
                'file': contents_file
            }
        )

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.json()['md5'], contents_md5)
        upload_to_hdfs.assert_called_once()

    @mock.patch('api.views.upload_to_hdfs')
    def test_file_post_wrong_md5(self, upload_to_hdfs):
        contents = b'filecontents'

        contents_md5 = md5(contents).hexdigest()
        contents_file = BytesIO()
        contents_file.write(contents)
        contents_file.seek(0)

        response = self.client.post(
            reverse('api-upload'),
            {
                'SECRET': settings.SECRET,
                'md5': 'wrongmd5',
                'method': 'cpf',
                'file': contents_file
            }
        )

        self.assertEquals(response.status_code, 500)
        self.assertEquals(response.json()['md5'], contents_md5)
        upload_to_hdfs.assert_not_called()
