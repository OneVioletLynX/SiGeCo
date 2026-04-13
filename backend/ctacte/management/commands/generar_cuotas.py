from django.core.management.base import BaseCommand
from datetime import date

from carreras.models import CarreraCursada
from ctacte.models import Cuota, MesPago, EstadoCuota


class Command(BaseCommand):

    help = "Genera las cuotas del mes actual para todos los alumnos activos"

    def handle(self, *args, **kwargs):

        hoy = date.today()

        anio = hoy.year
        mes = hoy.month

        # Solo generar cuotas marzo-diciembre
        if mes < 3:
            self.stdout.write("Mes fuera del ciclo académico")
            return

        mes_obj = MesPago.objects.filter(id_mes=mes).first()

        if not mes_obj:
            self.stdout.write("Mes no configurado en MesPago")
            return

        estado_pendiente = EstadoCuota.objects.get(descripcion="Pendiente")

        carreras = CarreraCursada.objects.filter(id_estado=1)

        generadas = 0

        for cc in carreras:

            _, created = Cuota.objects.get_or_create(
                alumno=cc.alumno,
                carrera=cc.carrera,
                mes=mes_obj,
                anio=anio,
                defaults={
                    "estado": estado_pendiente
                }
            )

            if created:
                generadas += 1

        self.stdout.write(
            f"Cuotas generadas: {generadas}"
        )