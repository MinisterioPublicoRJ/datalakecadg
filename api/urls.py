from django.urls import path
from .views import upload, upload_manual


urlpatterns = [
    path("upload/", upload, name="api-upload"),
    path("upload-manual", upload_manual, name="api-upload-manual"),
]
