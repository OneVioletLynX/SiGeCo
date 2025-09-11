from django.contrib import admin 
from django.urls import path 
from usuarios.views import UsuarioListCreate, UsuarioDetail 
urlpatterns = [ 
    path('admin/', admin.site.urls), 
    # Para listar y crear usuarios 
    path('api/usuarios/', UsuarioListCreate.as_view(), name='usuarios-lista'), 
    # Para operaciones sobre un usuario específico 
    path('api/usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detalle'), 
]
