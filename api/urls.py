from django.urls import path
from .views import cpf

urlpatterns = [
    path('cpf/', cpf, name='api-cpf')
]
