from django.contrib import admin 
from django.urls import path 
from usuarios.views import UsuarioListCreate, UsuarioDetail, LoginView
from alumnos.views import AlumnoListCreate, AlumnoDetail
from valores.views import ValoresListCreate, ValoresDetail, ConceptoListCreate, ConceptoDetail

urlpatterns = [ 
    path('admin/', admin.site.urls), 
    # Para listar y crear usuarios 
    path('api/usuarios/', UsuarioListCreate.as_view(), name='usuarios-lista'), 
    # Para operaciones sobre un usuario específico 
    path('api/usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detalle'), 
    path('api/login/', LoginView.as_view(), name='login'),

    path('api/alumnos/', AlumnoListCreate.as_view(), name='alumnos-lista'), 
    # Para operaciones sobre un alumnos específico 
    path('api/alumnos/<int:pk>/', AlumnoDetail.as_view(), name='alumno-detalle'), 

    path('api/valores/', ValoresListCreate.as_view(), name='valores-lista'), 
    path('api/valores/<int:pk>/', ValoresDetail.as_view(), name='valor-detalle'),    
    
    path('api/concepto/', ConceptoListCreate.as_view(), name='conceptos-lista'), 
    path('api/concepto/<int:pk>/', ConceptoDetail.as_view(), name='concepto-detalle'),    
]
