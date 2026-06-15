from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'config'


def redirigir_al_frontend(request):
    return redirect("http://127.0.0.1:8001/")


urlpatterns = [
    path('api/',   views.ConfigAPI.as_view(), name='api'),
    path('panel/', redirigir_al_frontend,     name='panel'),
]