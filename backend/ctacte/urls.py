from django.urls import path
from django.urls import path
from .views import ctacte_api_root
from .views import (
    ListaYCreaMesPago, DetalleMesPago,
    ListaYCreaMetodoPago, DetalleMetodoPago,
    ListaYCreaPago, DetallePago,
    ListaYCreaPagoDetalle, DetallePagoDetalle,
)

urlpatterns = [
    path('meses/', ListaYCreaMesPago.as_view(), name='mespago-list'),
    path('meses/<int:pk>/', DetalleMesPago.as_view(), name='mespago-detail'),

    path('metodos-pagos/', ListaYCreaMetodoPago.as_view(), name='metodopago-list'),
    path('metodos-pagos/<int:pk>/', DetalleMetodoPago.as_view(), name='metodopago-detail'),

    path('pagos/', ListaYCreaPago.as_view(), name='pago-list'),
    path('pagos/<int:pk>/', DetallePago.as_view(), name='pago-detail'),

    path('pagos-detalle/', ListaYCreaPagoDetalle.as_view(), name='pagodetalle-list'),
    path('pagos-detalle/<int:pk>/', DetallePagoDetalle.as_view(), name='pagodetalle-detail'),
    
    path('', ctacte_api_root, name='ctacte-root'),
]