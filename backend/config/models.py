from django.db import models
from django.utils import timezone


class ConfigInstituto(models.Model):
    """
    Configuración visual del instituto.
    Solo existe un registro (id=1).
    """
    nombre         = models.CharField(max_length=200, default="Centro Universitario")
    color_primario = models.CharField(max_length=7, default="#053D4E",
                                      help_text="Color hexadecimal principal, ej: #053D4E")
    creado         = models.DateTimeField(default=timezone.now)
    actualizado    = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table            = "config_instituto"
        managed             = False
        verbose_name        = "Configuración del Instituto"
        verbose_name_plural = "Configuración del Instituto"

    def __str__(self):
        return f"{self.nombre} ({self.color_primario})"

    @classmethod
    def get(cls):
        """Devuelve la configuración actual. Siempre usa id=1."""
        obj, _ = cls.objects.get_or_create(
            id=1,
            defaults={
                "nombre":         "Centro Universitario",
                "color_primario": "#053D4E",
            }
        )
        return obj