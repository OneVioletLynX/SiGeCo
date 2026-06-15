from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'usuarios'


def redirigir_al_frontend(request):
    return redirect("http://127.0.0.1:8001/")


urlpatterns = [
    # Rutas HTML legacy → redirigen al frontend
    path('', redirigir_al_frontend, name='login'),
    path('logout/', redirigir_al_frontend, name='logout'),
    path('admin/dashboard/', redirigir_al_frontend, name='admin_dashboard'),

    # API REST — login con JWT
    path('api/login/', views.api_login, name='api_login'),

    # API REST — gestión de usuarios (JWT, solo ADMIN)
    path('api/usuarios/', views.UsuarioAPIList.as_view(), name='api_usuarios_list'),
    path('api/usuarios/<int:pk>/', views.UsuarioAPIDetail.as_view(), name='api_usuarios_detail'),
]