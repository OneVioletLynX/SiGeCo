from django.urls import path
from . import views

app_name = 'usuarios_front'

urlpatterns = [
    path('', views.login_view, name='login'),
]
