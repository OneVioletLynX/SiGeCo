from django.urls import path
from . import views

app_name = 'usuarios_front'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('administracion/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('administracion/config/', views.admin_config, name='admin_config'),
]
