from django.apps import AppConfig
import os
class GeografiaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'geografia'

    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.geografia'
    else:
        name = 'geografia'

