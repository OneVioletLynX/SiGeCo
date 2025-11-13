import os
from django.apps import AppConfig

class AlumnosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Alumnos'

    # Detecta si se ejecuta desde el frontend o el backend
    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.alumnos'
    else:
        name = 'alumnos'
