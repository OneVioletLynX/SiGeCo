from django.urls import path
from .views import (
<<<<<<< HEAD
=======
    home_ctacte,
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
    ctacte_api_root,
    MesPagoListCreate, MesPagoDetail,
    MetodoPagoListCreate, MetodoPagoDetail,
    PagoListCreate, PagoDetail,
    PagoDetalleListCreate, PagoDetalleDetail,
    RegistrarPago,
<<<<<<< HEAD
    MesesPendientes,  
=======
    MesesPendientes
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
)

app_name = 'ctacte'

urlpatterns = [
<<<<<<< HEAD
=======
    # --- ROOT & FRONTEND ---
    # Ruta base de la app (ej: /ctacte/) -> Muestra el root de la API o el Home
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
    path('', ctacte_api_root, name='ctacte-root'),
    path('home/', home_ctacte, name='home'),

    # --- API ENDPOINTS ---

    # Meses de Pago
    path('meses/', MesPagoListCreate.as_view(), name='mespago-list'),
    path('meses/<int:pk>/', MesPagoDetail.as_view(), name='mespago-detail'),

    # Métodos de Pago
    path('metodos-pagos/', MetodoPagoListCreate.as_view(), name='metodopago-list'),
    path('metodos-pagos/<int:pk>/', MetodoPagoDetail.as_view(), name='metodopago-detail'),

    # Pagos (Cabecera)
    path('pagos/', PagoListCreate.as_view(), name='pago-list'),
    path('pagos/<int:pk>/', PagoDetail.as_view(), name='pago-detail'),

    # Detalles de Pagos (Items dentro del pago)
    path('pagos-detalle/', PagoDetalleListCreate.as_view(), name='pagodetalle-list'),
    path('pagos-detalle/<int:pk>/', PagoDetalleDetail.as_view(), name='pagodetalle-detail'),

    # --- FUNCIONALIDADES EXTRAS ---
    
    # Registrar un cobro completo (Lógica de negocio compleja)
    path('registrar-pago/', RegistrarPago.as_view(), name='registrar-pago'),
    
    # Consultar deudas o pendientes
    path('pendientes/', MesesPendientes.as_view(), name='ctacte-pendientes'),
<<<<<<< HEAD

]
=======
]
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
