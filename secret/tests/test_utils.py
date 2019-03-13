from unittest import TestCase

from freezegun import freeze_time

from secret.utils import create_secret


class Utils(TestCase):
    @freeze_time('2019-03-12 12:00:00')
    def test_create_secret_key(self):
        secret = create_secret()

        self.assertEqual(secret, 'd3a4646728a9de9a74d8fc4c41966a42')
