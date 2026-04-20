from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CarreraCursada


@receiver(post_save, sender=CarreraCursada)
def generar_cuota_inscripcion(sender, instance, created, **kwargs):
    """
    Cuando se crea una nueva CarreraCursada, genera automáticamente
    la cuota de Inscripcion (mes_id=1) como Pendiente.
    Usa get_or_create para evitar duplicados si se llama más de una vez.
    """
    if not created:
        return

    try:
        from ctacte.models import Cuota, MesPago, EstadoCuota
        from datetime import date

        mes_inscripcion  = MesPago.objects.filter(id_mes=1).first()
        estado_pendiente = EstadoCuota.objects.filter(descripcion="Pendiente").first()

        if not mes_inscripcion or not estado_pendiente:
            return

        anio = instance.anio_ingreso or date.today().year

        Cuota.objects.get_or_create(
            alumno=instance.alumno,
            carrera=instance.carrera,
            mes=mes_inscripcion,
            anio=anio,
            defaults={
                "estado":  estado_pendiente,
                "importe": 0,
            }
        )

    except Exception as e:
        # No romper el flujo de alta si falla la generación de cuota
        import logging
        logging.getLogger(__name__).warning(f"No se pudo generar cuota de inscripcion: {e}")