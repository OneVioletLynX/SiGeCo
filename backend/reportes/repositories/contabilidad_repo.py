from datetime import datetime, date
from django.db.models import Sum
from alumnos.models import Alumno
from carreras.models import CarreraCursada, Estado, Carrera
from ctacte.models import Pago, PagoDetalle, MetodoPago
from valores.models import Valor

#=====================================================
#                       KPIS
#=====================================================
def get_kpis_cont():
    hoy = datetime.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    # Ingresos del mes
    ingresos_mes = Pago.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes_actual).aggregate(total=Sum('importe_total'))['total'] or 0

    # Ingresos del año
    ingresos_anio = Pago.objects.filter(fecha_pago__year=anio_actual).aggregate(total=Sum('importe_total'))['total'] or 0

    #===========================
    #    CUOTAS COBRADAS
    #===========================
    cuotas_cobradas = PagoDetalle.objects.filter(pago__fecha_pago__year=anio_actual).count()
    from alumnos.models import Alumno

    # Alumnos con carrera activa
    estado_activo = Estado.objects.get(pk=1)
    alumnos_activos = Alumno.objects.filter(
        carreras_cursadas__id_estado=estado_activo
    ).distinct()
    cant_alumnos = alumnos_activos.count()
    
    total_de_cuotas_en_el_anio = cant_alumnos * 10
    cuotas_estimadas_anio = total_de_cuotas_en_el_anio - cuotas_cobradas

    # Tasa de morosidad
    tasa_morosidad = (cuotas_estimadas_anio / total_de_cuotas_en_el_anio * 100) if total_de_cuotas_en_el_anio else 0

    # ===========================
    #     ALUMNOS AL DÍA (CORREGIDO)
    # ===========================
    # Desde marzo hasta el mes actual
    meses_actuales = list(range(3, mes_actual + 1))
    # Todos los alumnos
    alumnos_que_pagaron = 0

    for alumno in alumnos_activos:
        # Pagos de este año
        pagos_actual = PagoDetalle.objects.filter(
            pago__id_alumno=alumno,
            mes__id_mes__in=meses_actuales,
            pago__fecha_pago__year=anio_actual
        ).values_list('mes', flat=True).distinct()

        # Verificar que esté al día
        if len(pagos_actual) == len(meses_actuales):
            alumnos_que_pagaron += 1

    porcentaje_alumnos_al_dia = (alumnos_que_pagaron / cant_alumnos * 100) if cant_alumnos else 0
    #===========================
    #    DATOS A PASAR
    #===========================
    data_kpis = {
        "kpis": {
            "ingresos_mes": f"${ingresos_mes:,.2f}",
            "ingresos_anio": f"${ingresos_anio:,.2f}",
            "cuotas_cobradas": cuotas_cobradas,
            "cuotas_estimadas_anio": cuotas_estimadas_anio,
            "tasa_morosidad": f"{tasa_morosidad:.2f}%",
            "alumnos_al_dia": f"{porcentaje_alumnos_al_dia:.2f}%"
        }
    }
    
    return data_kpis


#=====================================================
#                       CHARTS
#=====================================================

def get_charts_cont():
    anio_actual = datetime.now().year
    mes_actual = datetime.now().month
    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

    #===========================
    #     Ingresos mensuales
    #===========================
    ingresos_mensuales = []
    meses_ingresos = []

    for mes in range(3, mes_actual + 1):
        total_mes = Pago.objects.filter(fecha_pago__year=anio_actual, fecha_pago__month=mes).aggregate(total=Sum("importe_total"))["total"] or 0
        ingresos_mensuales.append(float(total_mes))
        meses_ingresos.append(meses_nombres[mes - 1])

    #===========================
    #     Medios de pago
    #===========================
    medios = MetodoPago.objects.all()
    medios_data = []

    for medio in medios:
        cantidad = Pago.objects.filter(id_metodo_pago=medio).count()
        medios_data.append({"value": cantidad, "name": medio.descripcion})

    #===========================
    #     Deuda por carrera (REVISADO Y CORREGIDO EL CÁLCULO)
    #===========================
    deuda_data = []
    nombres_carreras = []
    mes_inicio_ciclo = 3 
    cuotas_a_pagar_este_anio = max(0, mes_actual - mes_inicio_ciclo + 1) if mes_actual >= mes_inicio_ciclo else 0

    for carrera in Carrera.objects.all():
        nombres_carreras.append(carrera.descripcion)
        valor_cuota_obj = Valor.objects.filter(id_carrera=carrera).order_by("-modificacion").first()
        valor_cuota = valor_cuota_obj.importe if valor_cuota_obj else 0
        
        alumnos_en_carrera = CarreraCursada.objects.filter(carrera=carrera, id_estado__pk=1).select_related('alumno')
        
        deuda_total_carrera = 0
        cant_alumnos_con_deuda = 0

        for alumno_c_cursada in alumnos_en_carrera:
            alumno = alumno_c_cursada.alumno
            cuotas_esperadas_alumno = cuotas_a_pagar_este_anio 
            
            if cuotas_esperadas_alumno > 0:
                cant_alumnos_con_deuda += 1
                pagos_alumno_este_anio = PagoDetalle.objects.filter(
                    pago__id_alumno=alumno,
                    pago__fecha_pago__year=anio_actual,
                    mes__id_mes__gte=mes_inicio_ciclo,
                    mes__id_mes__lte=mes_actual
                ).aggregate(total=Sum("importe"))["total"] or 0
                monto_total_adeudado_teorico = valor_cuota * cuotas_esperadas_alumno

                deuda_alumno = max(monto_total_adeudado_teorico - pagos_alumno_este_anio, 0)
                deuda_total_carrera += deuda_alumno

        deuda_promedio_carrera = (deuda_total_carrera / cant_alumnos_con_deuda) if cant_alumnos_con_deuda > 0 else 0
        deuda_data.append(round(deuda_promedio_carrera, 2))

    #===========================
    #     Demora promedio
    #===========================
    demora_data = []
    meses_demora = []

    for mes_num in range(1, mes_actual + 1):
        meses_demora.append(meses_nombres[mes_num - 1])
        total_dias = 0
        total_pagos = 0
        pagos_en_el_mes = PagoDetalle.objects.filter(pago__fecha_pago__year=anio_actual, pago__fecha_pago__month=mes_num)
 
        for pago_detalle in pagos_en_el_mes:
            fecha_pago_real = pago_detalle.pago.fecha_pago.date() if isinstance(pago_detalle.pago.fecha_pago, datetime) else pago_detalle.pago.fecha_pago
            
            if not fecha_pago_real:
                continue

            # Vencimiento el día 1 
            fecha_vencimiento = date(anio_actual, pago_detalle.mes.id_mes, 1)
            
            dias_demora = max((fecha_pago_real - fecha_vencimiento).days, 0)
            total_dias += dias_demora
            total_pagos += 1

        demora_promedio = total_dias / total_pagos if total_pagos else 0
        demora_data.append(round(demora_promedio, 1))


    data_charts = {
        "meses_ingresos": meses_ingresos,
        "ingresos_mensuales": ingresos_mensuales,
        "medios_pago": medios_data,
        "carreras": nombres_carreras,
        "deuda_promedio": deuda_data,
        "meses_demora": meses_demora,
        "demora_mensual": demora_data
    }

    return data_charts