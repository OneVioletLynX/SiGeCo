from django.urls import path
from .views import index, MensajeListCreate, MensajeDetail

app_name = 'mensajes'

urlpatterns = [
    path('', index, name='index'), 
    path('api/', MensajeListCreate.as_view(), name='mensajes-list'),
        path('api/<int:pk>/', MensajeDetail.as_view(), name='mensajes-detail'),
]