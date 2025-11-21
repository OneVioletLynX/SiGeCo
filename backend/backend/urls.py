from django.contrib import admin 
from django.urls import path, include

# --- IMPORTACIONES ORGANIZADAS ---
# Usuarios
from usuarios.views import UsuarioListCreate, UsuarioDetail, LoginView
# Alumnos
from alumnos.views import AlumnoListCreate, AlumnoDetail
# Carreras
from carreras.views import (
    CarreraListCreate, CarreraDetail, 
    EstadoListCreate, EstadoDetail, 
    CarreraCursadasListCreate, CarreraCursadasDetail
)
# Valores
from valores.views import ValoresListCreate, ValoresDetail, ConceptoListCreate, ConceptoDetail
# Cta Cte (Pagos)
from ctacte.views import (
    MesPagoListCreate, MesPagoDetail, 
    MetodoPagoListCreate, MetodoPagoDetail, 
    PagoListCreate, PagoDetail, 
    PagoDetalleListCreate, PagoDetalleDetail
)
# Mensajes
from mensajes.views import MensajeListCreate, MensajeDetail
# Reportes (Vistas de función)
from reportes.views import seccion_contabilidad, seccion_alumnos, seccion_admin

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- USUARIOS ---
    path('api/usuarios/', UsuarioListCreate.as_view(), name='usuarios-lista'),
    path('api/usuarios/<int:pk>/', UsuarioDetail.as_view(), name='usuario-detalle'),
    path('api/login/', LoginView.as_view(), name='login'),

    # --- ALUMNOS ---
    path('api/alumnos/', AlumnoListCreate.as_view(), name='alumnos-lista'),
    path('api/alumnos/<int:pk>/', AlumnoDetail.as_view(), name='alumno-detalle'),

    # --- CARRERAS Y ESTADOS ---
    path('api/carreras/', CarreraListCreate.as_view(), name='carrera-lista'),
    path('api/carreras/<int:pk>/', CarreraDetail.as_view(), name='carrera-detalle'),
    
    path('api/estados/', EstadoListCreate.as_view(), name='estado-lista'),
    path('api/estados/<int:pk>/', EstadoDetail.as_view(), name='estado-detalle'),
    
    path('api/carreras-cursadas/', CarreraCursadasListCreate.as_view(), name='carreras-cursadas-lista'),
    path('api/carreras-cursadas/<int:alumno_id>/<int:carrera_id>/', CarreraCursadasDetail.as_view(), name='carreras-cursadas-detalle'),

    # --- VALORES Y CONCEPTOS ---
    path('api/valores/', ValoresListCreate.as_view(), name='valores-lista'),
    path('api/valores/<int:pk>/', ValoresDetail.as_view(), name='valor-detalle'),
    
    path('api/concepto/', ConceptoListCreate.as_view(), name='concepto-lista'),
    path('api/concepto/<int:pk>/', ConceptoDetail.as_view(), name='concepto-detalle'),

    # --- MENSAJES ---
    # API Endpoint
    path('api/mensajes/', MensajeListCreate.as_view(), name='api-mensajes'),
    path('api/mensajes/<int:pk>/', MensajeDetail.as_view(), name='api-mensajes-detail'),
    # Frontend / Template URL include
    path('mensajes/', include('mensajes.urls', namespace='mensajes')),

    # --- CTA CTE (PAGOS) ---
    path('api/mes-pago/', MesPagoListCreate.as_view(), name='mes-pago-lista'),
    path('api/mes-pago/<int:pk>/', MesPagoDetail.as_view(), name='mes-pago-detalle'),

    path('api/metodo-pago/', MetodoPagoListCreate.as_view(), name='metodo-pago-lista'),
    path('api/metodo-pago/<int:pk>/', MetodoPagoDetail.as_view(), name='metodo-pago-detalle'),
    
    path('api/pago/', PagoListCreate.as_view(), name='pago-lista'),
    path('api/pago/<int:pk>/', PagoDetail.as_view(), name='pago-detalle'),
    
    path('api/pago-detalle/', PagoDetalleListCreate.as_view(), name='pago-detalle-lista'),
    path('api/pago-detalle/<int:pago_id>/<int:mes_id>/', PagoDetalleDetail.as_view(), name='pago-detalle-detalle'),

    # Frontend / Template URL include para CtaCte
    path('ctacte/', include('ctacte.urls', namespace='ctacte')),

    # --- REPORTES / SECCIONES ---
    # Estas líneas estaban fuera de la lista (después del corchete), lo que causaba error.
    path('api/seccion/contabilidad/', seccion_contabilidad, name='seccion_contabilidad'), 
    path('api/seccion/alumnos/', seccion_alumnos, name='seccion_alumnos'), 
    path('api/seccion/administrativo/', seccion_admin, name='seccion_admin'), 

]