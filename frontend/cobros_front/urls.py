from django.urls import path
from . import views

app_name = 'cobros_front'

urlpatterns = [
    path('',        views.listado_cobros,      name='listado_cobros'),
    path('cobros/', views.cobros,              name='cobros'),
    path('comprobante/<int:id_pago>/', views.comprobante_cobro_pdf, name='comprobante_cobro_pdf'),
]