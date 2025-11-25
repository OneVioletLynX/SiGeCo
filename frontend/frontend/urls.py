from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('', include('carreras.urls')),
    path('', include('cobros.urls')),
    path('', include('alumnos.urls')),  
    path('', include('reportes.urls')),  
]