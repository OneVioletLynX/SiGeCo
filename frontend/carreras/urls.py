from django.urls import path
from . import views

app_name = 'carreras'

urlpatterns = [
    path('carreras/', views.carreras, name='carreras'),
]
