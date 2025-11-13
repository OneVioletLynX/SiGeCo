# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Alumno
# from carreras.models import CarreraCursada

# @receiver(post_save, sender=Alumno)
# def crear_carrera_por_defecto(sender, instance, created, **kwargs):
#     if not created:
#         return

#     carrera_id = getattr(instance, "_carrera_id", None)
#     print("[Signal DEBUG] Carrera recibida:", carrera_id)  # 👈 línea clave

#     if carrera_id:
#         CarreraCursada.objects.create(
#             alumno=instance,
#             carrera_id=carrera_id,
#             id_estado_id=1
#         )
