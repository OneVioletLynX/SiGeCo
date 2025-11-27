from django.contrib import admin
from django.urls import path, include

# --- IMPORTACIONES ---

# 1. Usuarios (CORREGIDO: Importamos el módulo completo)
from usuarios import views as usuarios_views

# 2. Alumnos
from alumnos.views import AlumnoListCreate, AlumnoDetail

# 3. Carreras
from carreras.views import (
    CarreraListCreate, CarreraDetail, 
    EstadoListCreate, EstadoDetail, 
    CarreraCursadasListCreate, CarreraCursadasDetail
)

# 4. Valores
from valores.views import (
    ValoresListCreate, ValoresDetail, 
    ConceptoListCreate, ConceptoDetail, 
    ValorVigenteView
)

# 5. Cta Cte (Pagos)
from ctacte.views import (
    MesPagoListCreate, MesPagoDetail, 
    MetodoPagoListCreate, MetodoPagoDetail, 
    PagoListCreate, PagoDetail, 
    PagoDetalleListCreate, PagoDetalleDetail
)

# 6. Reportes
from reportes.views import seccion_contabilidad, seccion_alumnos, seccion_admin


urlpatterns = [
    # -------------------------------------------------------
    # 1. LOGIN Y ADMIN
    # -------------------------------------------------------
    # Al entrar a http://127.0.0.1:8001/ se abre el LOGIN
    path('', usuarios_views.login_view, name='home'),
    
    # Rutas internas de la app usuarios (logout, dashboard)
    path('usuarios/', include('usuarios.urls')),
    
    # Admin de Django
    path('admin/', admin.site.urls),


    # -------------------------------------------------------
    # 2. APPS PRINCIPALES (Con Frontend propio)
    # -------------------------------------------------------
    # Mensajes (Index + su propia API interna)
    path('mensajes/', include('mensajes.urls')),
    
    # Cta Cte (Index + su propia API interna)
    path('ctacte/', include('ctacte.urls')),


    # -------------------------------------------------------
    # 3. API GLOBAL (Endpoins sueltos para Select2/AJAX)
    # -------------------------------------------------------
    
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
    path('api/valores/vigente/', ValorVigenteView.as_view(), name='valor-vigente'),
    
    path('api/concepto/', ConceptoListCreate.as_view(), name='concepto-lista'),
    path('api/concepto/<int:pk>/', ConceptoDetail.as_view(), name='concepto-detalle'),

    # --- CTA CTE (API ENDPOINTS SUELTOS) ---
    path('api/mes-pago/', MesPagoListCreate.as_view(), name='mes-pago-lista'),
    path('api/mes-pago/<int:pk>/', MesPagoDetail.as_view(), name='mes-pago-detalle'),

    path('api/metodo-pago/', MetodoPagoListCreate.as_view(), name='metodo-pago-lista'),
    path('api/metodo-pago/<int:pk>/', MetodoPagoDetail.as_view(), name='metodo-pago-detalle'),
    
    path('api/pago/', PagoListCreate.as_view(), name='pago-lista'),
    path('api/pago/<int:pk>/', PagoDetail.as_view(), name='pago-detalle'),
    
    path('api/pago-detalle/', PagoDetalleListCreate.as_view(), name='pago-detalle-lista'),
    path('api/pago-detalle/<int:pago_id>/<int:mes_id>/', PagoDetalleDetail.as_view(), name='pago-detalle-detalle'),

    # --- REPORTES ---
    path('api/seccion/contabilidad/', seccion_contabilidad, name='seccion_contabilidad'), 
    path('api/seccion/alumnos/', seccion_alumnos, name='seccion_alumnos'), 
    path('api/seccion/administrativo/', seccion_admin, name='seccion_admin'), 
]