from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios_front.urls')),
    path('', include('carreras_front.urls')),
    path('', include('cobros_front.urls')),
<<<<<<< HEAD
    path('', include('reportes.urls')),  
=======
>>>>>>> 1c988ca79943e86bcb4fca0a65d0e2eb6e2ecb53
    path('', include('alumnos_front.urls')),  
]