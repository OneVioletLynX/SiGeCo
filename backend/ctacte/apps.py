import os
from django.apps import AppConfig

class CtacteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Cuentas Corrientes'

    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.ctacte'
    else:
        name = 'ctacte'
