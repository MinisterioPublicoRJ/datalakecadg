from django.urls import path
from .views import home, upload_manual


app_name = 'core'
urlpatterns = [
    path('', home, name='home'),
    path("upload-manual", upload_manual, name="upload-manual"),
]
