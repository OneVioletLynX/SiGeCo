from django.contrib import admin 
from django.urls import path, include
from usuarios.views import UsuarioListCreate, UsuarioDetail, LoginView
from alumnos.views import AlumnoListCreate, AlumnoDetail
from carreras.views import CarreraListCreate, CarreraDetail, EstadoListCreate, EstadoDetail, CarreraCursadasListCreate, CarreraCursadasDetail
from valores.views import ValoresListCreate, ValoresDetail, ConceptoListCreate, ConceptoDetail, ValorVigenteView
from ctacte.views import MesPagoListCreate, MesPagoDetail, MetodoPagoListCreate, MetodoPagoDetail, PagoDetail, PagoListCreate, PagoDetalleListCreate, PagoDetalleDetail, MesPagoDetail
from django.urls import path, include
from mensajes.views import MensajeListCreate, MensajeDetail
from mensajes.views import MensajeListCreate 
from reportes.views import seccion_contabilidad, seccion_alumnos, seccion_admin
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

    path('api/valores/', ValoresListCreate.as_view(), name='valores-lista'), 
    path('api/valores/<int:pk>/', ValoresDetail.as_view(), name='valor-detalle'),    
    path('api/valores/vigente/', ValorVigenteView.as_view(), name='valor-vigente'),

    path('api/concepto/', ConceptoListCreate.as_view(), name='concepto-lista'), 
    path('api/concepto/<int:pk>/', ConceptoDetail.as_view(), name='concepto-detalle'),  

    path('api/mes-pago/', MesPagoListCreate.as_view(), name='mes-pago-lista'), 
    path('api/mes-pago/<int:pk>/', MesPagoDetail.as_view(), name='mes-pago-detalle'), 

    path('api/metodo-pago/', MetodoPagoListCreate.as_view(), name='metodo-pago-lista'), 
    path('api/metodo-pago/<int:pk>/', MetodoPagoDetail.as_view(), name='metodo-pago-detalle'),  

    path('api/pago/', PagoListCreate.as_view(), name='pago-lista'), 
    path('api/pago/<int:pk>/', PagoDetail.as_view(), name='pago-detalle'),  

    #path('api/login/', ConceptoListCreate.as_view(), name='login-lista'), 
    #path('api/login/<int:pk>/', ConceptoDetail.as_view(), name='login-detalle'),     

    path('api/pago-detalle/', PagoDetalleListCreate.as_view(), name='pago-detalle-lista'), 
    # Para operaciones sobre carreras-cursadas
    path('api/pago-detalle/<int:pago_id>/<int:mes_id>/', PagoDetalleDetail.as_view(), name='pago-detalle-detalle'),
    #Estadisticas
    path('api/seccion/contabilidad/', seccion_contabilidad, name='seccion_contabilidad'), 
    path('api/seccion/alumnos/', seccion_alumnos, name='seccion_alumnos'), 
    path('api/seccion/administrativo/', seccion_admin, name='seccion_admin'), 
    # Mensajes
    path('api/mensajes/', MensajeListCreate.as_view(), name='api-mensajes'),
    path('api/mensajes/<int:pk>/', MensajeDetail.as_view(), name='api-mensajes-detail'),
    path('mensajes/', include('mensajes.urls', namespace='mensajes')),

    # CTActe: frontend + API
    path('ctacte/', include('ctacte.urls', namespace='ctacte')),
]