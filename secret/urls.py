from django.urls import path

from secret.views import create_secret, list_secret


app_name = 'secret'
urlpatterns = [
    path('create/', create_secret, name='create-secret'),
    path('list/', list_secret, name='list-secret'),
]
