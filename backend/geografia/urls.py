from django.urls import path
from .views import ProvinciaList, LocalidadPorProvincia

urlpatterns = [
    path("provincias/", ProvinciaList.as_view()),
    path("localidades/", LocalidadPorProvincia.as_view()),
]