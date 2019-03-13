from django.urls import path, re_path

from secret.views import create_secret, list_secret, delete_secret


app_name = 'secret'
urlpatterns = [
    path('create/', create_secret, name='create-secret'),
    path('list/', list_secret, name='list-secret'),
    re_path(
        r'^delete/(?P<pk>[a-f0-9]{32})/$',
        delete_secret,
        name='delete-secret'
    ),
]
