# from django.urls import path
# from django.urls import path
# from .views import ctacte_api_root
# from .views import MesPagoListCreate
# from .views import home_ctacte

# from .views import (
#     ctacte_api_root,
#     MesPagoListCreate, MesPagoDetail,
#     MetodoPagoListCreate, MetodoPagoDetail,
#     PagoListCreate, PagoDetail,
#     PagoDetalleListCreate, PagoDetalleDetail,
# )


# urlpatterns = [
#     path('meses/', MesPagoListCreate.as_view(), name='mespago-list'),
#     path('meses/<int:pk>/', MesPagoDetail.as_view(), name='mespago-detail'),

#     path('metodos-pagos/', MetodoPagoListCreate.as_view(), name='metodopago-list'),
#     path('metodos-pagos/<int:pk>/', MetodoPagoDetail.as_view(), name='metodopago-detail'),

#     path('pagos/', PagoListCreate.as_view(), name='pago-list'),
#     path('pagos/<int:pk>/', PagoDetail.as_view(), name='pago-detail'),

#     path('pagos-detalle/', PagoDetalleListCreate.as_view(), name='pagodetalle-list'),
#     path('pagos-detalle/<int:pk>/', PagoDetalleDetail.as_view(), name='pagodetalle-detail'),

#     path('', ctacte_api_root, name='ctacte-root'),
    
#     path('home/', home_ctacte, name='home_ctacte')
# ]

#NUEVO:

from django.urls import path
from .views import (
    home_ctacte,
    ctacte_api_root,
    MesPagoListCreate, MesPagoDetail,
    MetodoPagoListCreate, MetodoPagoDetail,
    PagoListCreate, PagoDetail,
    PagoDetalleListCreate, PagoDetalleDetail
)

app_name = 'ctacte'

urlpatterns = [
    # FRONTEND
    path('', home_ctacte, name='home'),

    # API
    path('api/', ctacte_api_root, name='api-root'),
    path('api/meses/', MesPagoListCreate.as_view(), name='meses-list'),
    path('api/meses/<int:pk>/', MesPagoDetail.as_view(), name='meses-detail'),
    path('api/metodos-pagos/', MetodoPagoListCreate.as_view(), name='metodos-list'),
    path('api/metodos-pagos/<int:pk>/', MetodoPagoDetail.as_view(), name='metodos-detail'),
    path('api/pagos/', PagoListCreate.as_view(), name='pagos-list'),
    path('api/pagos/<int:pk>/', PagoDetail.as_view(), name='pagos-detail'),
    path('api/pagos-detalle/', PagoDetalleListCreate.as_view(), name='pagos-detalle-list'),
    path('api/pagos-detalle/<int:pk>/', PagoDetalleDetail.as_view(), name='pagos-detalle-detail'),
]




# urlpatterns = [
#     # Nombres (name) ajustados para que coincidan con los usados en views.reverse()
#     path('meses/', MesPagoListCreate.as_view(), name='meses-list'),
#     path('meses/<int:pk>/', MesPagoDetail.as_view(), name='meses-detail'),

#     path('metodos-pagos/', MetodoPagoListCreate.as_view(), name='metodos-list'),
#     path('metodos-pagos/<int:pk>/', MetodoPagoDetail.as_view(), name='metodos-detail'),

#     path('pagos/', PagoListCreate.as_view(), name='pagos-list'),
#     path('pagos/<int:pk>/', PagoDetail.as_view(), name='pagos-detail'),

#     path('pagos-detalle/', PagoDetalleListCreate.as_view(), name='pagos-detalle-list'),
#     path('pagos-detalle/<int:pk>/', PagoDetalleDetail.as_view(), name='pagos-detalle-detail'),

#     path('', ctacte_api_root, name='ctacte-root'),
#     path('home/', home_ctacte, name='home_ctacte'),
    
#     #  path('pagos/', views.PagosListView.as_view(), name='pagos-list'),
#     path('pagos/', views.PagoListCreate.as_view(), name='pagos-list'),

# ]