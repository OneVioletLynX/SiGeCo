from django.contrib import admin 
from django.urls import path 
from usuarios.views import UsuarioListCreate, UsuarioDetail
from alumnos.views import AlumnoListCreate, AlumnoDetail

urlpatterns = [ 
    path('admin/', admin.site.urls), 
    # Para listar y crear usuarios 
    path('api/usuarios/', UsuarioListCreate.as_view(), name='usuarios-lista'), 
    # Para operaciones sobre un usuario específico 
    path('api/usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detalle'), 

    path('api/alumnos/', AlumnoListCreate.as_view(), name='alumnos-lista'), 
    # Para operaciones sobre un alumnos específico 
    path('api/alumnos/<int:pk>/', AlumnoDetail.as_view(), name='alumno-detalle'), 
    
]
