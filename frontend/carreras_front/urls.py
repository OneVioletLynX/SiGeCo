from django.urls import path
from . import views

app_name = 'carreras_front'

urlpatterns = [
    path('carreras/', views.carreras, name='carreras'),
]
