from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios_front.urls')),
    path('', include('carreras_front.urls')),
    path('', include('cobros_front.urls')),
    path('', include('alumnos_front.urls')),  
]