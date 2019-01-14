from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from .decorators import securedecorator

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
