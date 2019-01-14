from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from hashlib import md5
from .utils import securedecorator, md5reader

# Create your tests here.

@securedecorator
def postmethod(request):
    pass

class TestSecureDecorator(TestCase):
    def test_secure_empty_key(self):
        fakerequest = RequestFactory().post('')

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)

    def test_secure_wrong_key(self):
        fakerequest = RequestFactory().post(
            '',
            data={'SECRET': 'wrongkey'}
        )
        

        with self.assertRaises(PermissionDenied):
            postmethod(request=fakerequest)


    def test_secure(self):
        fakerequest = RequestFactory().post(
            '',
            data={'SECRET': settings.SECRET}
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

    def test_wronghexdigest(self):
        uploadedfile = SimpleUploadedFile(
            'file',
            b'filecontents'
        )

        self.assertNotEquals(
            md5reader(uploadedfile),
            md5(b'lerolero').hexdigest()
        )
