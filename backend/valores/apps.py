import os
from django.apps import AppConfig

class ValoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Valores'

    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.valores'
    else:
        name = 'valores'
