import os
from django.apps import AppConfig


class CarrerasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    verbose_name = 'Carreras'

    if os.path.basename(os.getcwd()) == 'frontend':
        name = 'backend.carreras'
    else:
        name = 'carreras'

    def ready(self):  # ← adentro de la clase, con indentación
        try:
            import carreras.signals  # noqa: F401
        except ModuleNotFoundError:
            import backend.carreras.signals  # noqa: F401