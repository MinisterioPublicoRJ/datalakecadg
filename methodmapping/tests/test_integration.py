import json
import os
from datetime import date as dt
from hashlib import md5
from unittest import mock, skipIf

from decouple import config
from django.test import TestCase
from django.urls import reverse
from model_mommy.mommy import make
from unipath import Path

from api.clients import hdfsclient


FIXTURES_DIR = Path(__file__).parent.child("fixtures")


class DatabaseIntegrationTest(TestCase):
    @skipIf(
        config("SKIP_INTEGRATION_TESTS", True, cast=bool),
        "Skipping integration test!"
    )
    @mock.patch("secret.models.login")
    def test_hdfs_integrations_test(self, _login):
        # TEST CONFIG
        filepath = config(
            "INTEGRATION_TEST_FILEPATH",
            FIXTURES_DIR.child("integration_test_file.csv.gz")
        )
        method = config("INTEGRATION_TEST_METHOD_NAME")
        username = config("INTEGRATION_TEST_USERNAME")
        secret_key = config("INTEGRATION_TEST_SECRET_KEY")
        hdfs_uri = config("INTEGRATION_TEST_HDFS_URI")
        schema_path = config(
            "INTEGRATION_TEST_SCHEMA_PATH",
            FIXTURES_DIR.child("integration_test_schema.json")
        )

        with open(schema_path) as fobj:
            schema = json.load(fobj)

        secret_obj = make(
            "secret.Secret",
            username=username,
            secret_key=secret_key
        )
        method_obj = make(
            "methodmapping.MethodMapping",
            method=method,
            uri=hdfs_uri,
            schema=schema
        )
        secret_obj.methods.add(method_obj)
        secret_obj.save()

        filename = f'integration_test_{dt.today()}.csv.gz'
        with open(filepath, mode="rb") as file_:
            contents_md5 = md5(file_.read()).hexdigest()
            file_.seek(0)
            response = self.client.post(
                reverse('api-upload'),
                {
                    'SECRET': secret_key,
                    'nome': username,
                    'md5': contents_md5,
                    'method': method,
                    'file': file_,
                    'filename': filename
                }
            )

        print(response.json())
        self.assertEqual(response.status_code, 201)
        hdfsclient.status(os.path.join(hdfs_uri, username, filename))
