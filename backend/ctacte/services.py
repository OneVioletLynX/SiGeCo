from datetime import date
from carreras.models import CarreraCursada
from valores.models import Valor
from ctacte.models import Cuota, MesPago, EstadoCuota

# Nueva tabla ctacte_mespago:
# 1  = Inscripcion
# 2  = Marzo
# 3  = Abril
# 4  = Mayo
# 5  = Junio
# 6  = Julio
# 7  = Agosto
# 8  = Septiembre
# 9  = Octubre
# 10 = Noviembre
# 11 = Diciembre

# Todos los id_mes válidos del sistema
MESES_CICLO = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

# Los que corresponden a meses calendario reales (para validar "mes futuro")
# Inscripcion (1) no es mes calendario, se excluye
MESES_CALENDARIO = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11}

# Mapeo id_mes → número de mes calendario real (para buscar valores vigentes)
MES_A_CALENDARIO = {
    1: 1,   # Inscripcion → usa enero como referencia
    2: 3,   # Marzo
    3: 4,   # Abril
    4: 5,   # Mayo
    5: 6,   # Junio
    6: 7,   # Julio
    7: 8,   # Agosto
    8: 9,   # Septiembre
    9: 10,  # Octubre
    10: 11, # Noviembre
    11: 12, # Diciembre
}


def generar_cuotas_mes(anio=None, mes=None):
    """
    Genera las cuotas del mes indicado para todos los alumnos con carreras activas.
    'mes' es el id_mes de ctacte_mespago (1=Inscripcion, 2=Marzo, ..., 11=Diciembre).
    """
    hoy  = date.today()
    anio = anio or hoy.year
    mes  = mes  or hoy.month  # por defecto usa el mes calendario actual

    if mes not in MESES_CICLO:
        return {"generadas": 0, "motivo": f"Mes {mes} fuera del ciclo académico."}

    mes_obj = MesPago.objects.filter(id_mes=mes).first()
    if not mes_obj:
        return {"generadas": 0, "motivo": f"Mes con id={mes} no está configurado en MesPago."}

    try:
        estado_pendiente = EstadoCuota.objects.get(descripcion="Pendiente")
    except EstadoCuota.DoesNotExist:
        return {"generadas": 0, "motivo": "No existe el estado 'Pendiente' en EstadoCuota."}

    carreras_activas = CarreraCursada.objects.filter(
        id_estado=1
    ).select_related("alumno", "carrera")

    generadas = 0

    for cc in carreras_activas:
        importe = _obtener_importe_vigente(cc.carrera_id, anio, mes)

        _, created = Cuota.objects.get_or_create(
            alumno=cc.alumno,
            carrera=cc.carrera,
            mes=mes_obj,
            anio=anio,
            defaults={
                "estado": estado_pendiente,
                "importe": importe,
            }
        )
        if created:
            generadas += 1

    return {"generadas": generadas}


def _obtener_importe_vigente(carrera_id, anio, id_mes):
    """
    Busca el valor vigente para una carrera dado un año e id_mes.
    Convierte el id_mes al mes calendario real para buscar en Valor.
    """
    mes_cal = MES_A_CALENDARIO.get(id_mes, 1)
    fecha_ref = date(anio, mes_cal, 1)

    valor = (
        Valor.objects
        .filter(
            id_carrera_id=carrera_id,
            id_concepto=1,
            fecha_inicio__lte=fecha_ref,
        )
        .order_by("-fecha_inicio")
        .first()
    )

    return valor.importe if valor else 0