from django.urls import path
from . import views

app_name = 'mensajes_front'

urlpatterns = [
    path('mensajes', views.mensajes, name='mensajes'), 
]