from datetime import date
from carreras.models import CarreraCursada
from ctacte.models import Cuota, MesPago, EstadoCuota


def generar_cuotas_mes():

    hoy = date.today()
    anio = hoy.year
    mes_actual = hoy.month

    estado_pendiente = EstadoCuota.objects.get(descripcion="Pendiente")

    carreras = CarreraCursada.objects.select_related("alumno", "carrera")

    for cc in carreras:

        mes_obj = MesPago.objects.filter(id_mes=mes_actual).first()

        if not mes_obj:
            continue

        Cuota.objects.get_or_create(
            alumno=cc.alumno,
            carrera=cc.carrera,
            mes=mes_obj,
            anio=anio,
            defaults={
                "estado": estado_pendiente,
                "importe": 0
            }
        )