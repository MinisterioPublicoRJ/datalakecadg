from django.test import TestCase

from methodmapping.helpers import header_to_schema


class PopulateSchemaTest(TestCase):
    def test_transform_madatory_headers_to_schema(self):
        mandatory_headers = "field1,field2,field3"

        schema = header_to_schema(mandatory_headers)
        expected = {
            "fields": [
                {"name": "field1"},
                {"name": "field2"},
                {"name": "field3"},
            ]
        }

        self.assertEqual(schema, expected)
