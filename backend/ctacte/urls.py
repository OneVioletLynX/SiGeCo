from django.urls import path
from .views import (
    home_ctacte,
    ctacte_api_root,
    MesPagoListCreate, MesPagoDetail,
    MetodoPagoListCreate, MetodoPagoDetail,
    PagoListCreate, PagoDetail,
    PagoDetalleListCreate, PagoDetalleDetail,
    RegistrarPago,
    MesesPendientes,  
)

app_name = 'ctacte'

urlpatterns = [
    path('', ctacte_api_root, name='ctacte-root'),

    # Meses
    path('meses/', MesPagoListCreate.as_view(), name='mespago-list'),
    path('meses/<int:pk>/', MesPagoDetail.as_view(), name='mespago-detail'),

    # Métodos de pago
    path('metodos-pagos/', MetodoPagoListCreate.as_view(), name='metodopago-list'),
    path('metodos-pagos/<int:pk>/', MetodoPagoDetail.as_view(), name='metodopago-detail'),

    # Pagos
    path('pagos/', PagoListCreate.as_view(), name='pago-list'),
    path('pagos/<int:pk>/', PagoDetail.as_view(), name='pago-detail'),

    # Pago detalle
    path('pagos-detalle/', PagoDetalleListCreate.as_view(), name='pagodetalle-list'),
    path('pagos-detalle/<int:pk>/', PagoDetalleDetail.as_view(), name='pagodetalle-detail'),

    # Registrar un cobro completo (Pago + Detalles)
    path('registrar-pago/', RegistrarPago.as_view(), name='registrar-pago'),
    path('pendientes/', MesesPendientes.as_view(), name='ctacte-pendientes'),

]
