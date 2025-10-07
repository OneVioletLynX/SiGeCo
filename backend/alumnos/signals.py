# alumnos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alumno
from carreras.models import CarreraCursada

@receiver(post_save, sender=Alumno)
def crear_carrera_por_defecto(sender, instance, created, **kwargs):
    if created:
        CarreraCursada.objects.create(
            alumno=instance,
            # carrera por defecto id=1
            carrera_id=1,
            # estado por defecto id=1
            id_estado_id=1
        )
