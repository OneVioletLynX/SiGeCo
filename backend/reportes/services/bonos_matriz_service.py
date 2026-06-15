from carreras.models import CarreraCursada
from ctacte.models import PagoDetalle, MesPago

CONCEPTO_CUOTA_ID = 1


def bonos_matriz_data(carrera_id, anio, mostrar_ingresantes=True):
    meses_qs = list(MesPago.objects.order_by('id_mes').values('id_mes', 'descripcion'))
    mes_ids    = [m['id_mes']     for m in meses_qs]
    mes_nombres = [m['descripcion'] for m in meses_qs]

    cursadas = (
        CarreraCursada.objects
        .filter(carrera_id=carrera_id)
        .select_related('alumno')
        .order_by('alumno__apellido', 'alumno__nombre')
    )

    if not mostrar_ingresantes:
        cursadas = cursadas.exclude(anio_ingreso=anio)

    detalles = PagoDetalle.objects.filter(
        carrera_id=carrera_id,
        anio_pago=anio,
        id_concepto=CONCEPTO_CUOTA_ID,
    ).values('pago__id_alumno_id', 'mes_id')

    pagos_dict = {}
    for d in detalles:
        alumno_id = d['pago__id_alumno_id']
        if alumno_id not in pagos_dict:
            pagos_dict[alumno_id] = set()
        pagos_dict[alumno_id].add(d['mes_id'])

    alumnos_data = []
    for cursada in cursadas:
        alumno = cursada.alumno
        meses_pagados = pagos_dict.get(alumno.id_alumno, set())
        pagos_row = [m_id in meses_pagados for m_id in mes_ids]
        alumnos_data.append({
            'legajo': alumno.legajo or '-',
            'nombre': f"{alumno.apellido}, {alumno.nombre}",
            'es_ingresante': cursada.anio_ingreso == anio,
            'pagos': pagos_row,
            'total_pagados': sum(pagos_row),
        })

    return {
        'meses': mes_nombres,
        'alumnos': alumnos_data,
    }
