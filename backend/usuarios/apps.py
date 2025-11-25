import os
from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Usuarios'

    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.usuarios'
    else:
        name = 'usuarios'
