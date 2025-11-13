from django.contrib import admin 
from django.urls import path 
from usuarios.views import UsuarioListCreate, UsuarioDetail
from alumnos.views import AlumnoListCreate, AlumnoDetail
from carreras.views import CarreraListCreate, CarreraDetail, EstadoListCreate, EstadoDetail, CarreraCursadasListCreate, CarreraCursadasDetail
from valores.views import ValoresListCreate, ValoresDetail, ConceptoListCreate, ConceptoDetail
from ctacte.views import MesPagoListCreate, MesPagoDetail, MetodoPagoListCreate, MetodoPagoDetail, PagoDetail, PagoListCreate, PagoDetalleListCreate, PagoDetalleDetail, MesPagoDetail
from django.urls import path, include
from mensajes.views import MensajeListCreate, MensajeDetail
# from ctacte.views import CtacteList 
from mensajes.views import MensajeListCreate 
urlpatterns = [
    path('admin/', admin.site.urls),

    # Usuarios
    path('api/usuarios/', UsuarioListCreate.as_view(), name='usuarios-lista'),
    path('api/usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detalle'),

    # Alumnos
    path('api/alumnos/', AlumnoListCreate.as_view(), name='alumnos-lista'),
    path('api/alumnos/<int:pk>/', AlumnoDetail.as_view(), name='alumno-detalle'),

    # Carreras y estados
    path('api/carreras/', CarreraListCreate.as_view(), name='carrera-lista'),
    path('api/carreras/<int:pk>/', CarreraDetail.as_view(), name='carrera-detalle'),
    path('api/estados/', EstadoListCreate.as_view(), name='estado-lista'),
    path('api/estados/<int:pk>/', EstadoDetail.as_view(), name='estado-detalle'),
    path('api/carreras-cursadas/', CarreraCursadasListCreate.as_view(), name='carreras-cursadas-lista'),
    path('api/carreras-cursadas/<int:alumno_id>/<int:carrera_id>/', CarreraCursadasDetail.as_view(), name='carreras-cursadas-detalle'),

    # Valores y conceptos
    path('api/valores/', ValoresListCreate.as_view(), name='valores-lista'),
    path('api/valores/<int:pk>/', ValoresDetail.as_view(), name='valor-detalle'),
    path('api/concepto/', ConceptoListCreate.as_view(), name='concepto-lista'),
    path('api/concepto/<int:pk>/', ConceptoDetail.as_view(), name='concepto-detalle'),

    # Mensajes
    path('api/mensajes/', MensajeListCreate.as_view(), name='api-mensajes'),
    path('api/mensajes/<int:pk>/', MensajeDetail.as_view(), name='api-mensajes-detail'),
    path('mensajes/', include('mensajes.urls', namespace='mensajes')),

    # CTActe: frontend + API
    path('ctacte/', include('ctacte.urls', namespace='ctacte')),
]
