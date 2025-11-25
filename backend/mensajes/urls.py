from django.urls import path
from .views import index, MensajeListCreate, MensajeDetail

app_name = 'mensajes'

urlpatterns = [
    # Esta ruta es para tu plantilla HTML, la dejamos como está.
    # (Asumiendo que la incluyes como 'mensajes/' en tu urls.py principal)
    path('', index, name='index'), 
    
    # CAMBIO AQUÍ: 'api/' -> 'api/mensajes/'
    path('api/mensajes/', MensajeListCreate.as_view(), name='mensajes-list'),
    
    # CAMBIO AQUÍ: 'api/<int:pk>/' -> 'api/mensajes/<int:pk>/'
    path('api/mensajes/<int:pk>/', MensajeDetail.as_view(), name='mensajes-detail'),
]