from django.contrib import admin
from django.urls import path, include
from .views import home

urlpatterns = [
    path('inicio/', home, name='home'),  # 🟢 Home principal

    # Secciones con prefijo
    path('carreras/', include('carreras_front.urls')),
    path('cobros/', include('cobros_front.urls')),
    path('alumnos/', include('alumnos_front.urls')),
    path('reportes/', include('reportes.urls')),
    path('mensajes/', include("mensajes_front.urls")),
    path('', include("usuarios_front.urls")),

    # Admin
    path('admin/', admin.site.urls),
]
