from django.urls import path
from . import views

app_name = 'alumnos'

urlpatterns = [
    path('alumnos/', views.alumnos, name='alumnos'),
]
