from datetime import datetime, date
from django.db.models import Count, Max, Min, Case, When, IntegerField, F
from alumnos.models import Alumno
from carreras.models import CarreraCursada, Carrera, Estado
from django.db.models.functions import ExtractYear
from ctacte.models import Pago, PagoDetalle, MesPago
from django.utils import timezone
from django.db.models.functions import ExtractYear

#=====================================================
#                       KPIS
#=====================================================

def get_kpis_alumnos():
    ID_ACTIVO = 1
    ID_FINALIZADO = 4
    anio_actual = timezone.now().year
    anio_anterior = anio_actual - 1
    
    # ===========================
    #   ALUMNOS ACTIVOS
    # ===========================
    alumnos_activos_ids = CarreraCursada.objects.filter(
        id_estado__id_estado=ID_ACTIVO 
    ).values_list('alumno_id', flat=True).distinct()
    cant_alumnos_activos = alumnos_activos_ids.count()

    # ===========================
    #       EGRESADOS
    # ===========================
    try:
        id_estado_egresado = Estado.objects.get(descripcion__iexact='Finalizado').id_estado
    except Estado.DoesNotExist:
        id_estado_egresado = ID_FINALIZADO

    cant_alumnos_egresados = CarreraCursada.objects.filter(
        id_estado__id_estado=id_estado_egresado 
    ).values('alumno_id').distinct().count()
    
    # ===========================
    #       INGRESANTES
    # ===========================
    cant_alumnos_ingresantes = Alumno.objects.filter(
        anio_ingreso=anio_actual
    ).count()

    # ==================================
    #       TASA DE RETENCIÓN
    # ==================================
    
    # Alumnos que debieron continuar
    alumnos_base_anterior_ids = Alumno.objects.filter(
        anio_ingreso__lte=anio_anterior
    ).values_list('id_alumno', flat=True).distinct()
    cant_base_anterior = alumnos_base_anterior_ids.count()

    # Alumnos Retenidos (Activos de la base anterior)
    alumnos_retenidos_ids = list(
        set(alumnos_activos_ids) & set(alumnos_base_anterior_ids)
    )
    cant_retenidos = len(alumnos_retenidos_ids)

    # Cálculo de la tasa
    if cant_base_anterior > 0:
        tasa_retencion = (cant_retenidos / cant_base_anterior) * 100
    else:
        tasa_retencion = 0
    tasa_retencion_fmt = f"{tasa_retencion:.2f}%"

    # ==================================
    #   PROMEDIO AÑOS DE PERMANENCIA 
    # ==================================
    
    permanencia_data = Alumno.objects.filter(
        pago__fecha_pago__isnull=False
    ).annotate(
        fecha_inicio=Min('pago__fecha_pago'),
        fecha_fin=Max('pago__fecha_pago'),
    ).distinct().values('fecha_inicio', 'fecha_fin', 'id_alumno')

    total_meses = 0
    total_alumnos = 0
    
    for item in permanencia_data:
        fecha_fin_real = item['fecha_fin']
        
        if item['fecha_inicio'] and fecha_fin_real:
            # Cálculo de meses
            diff = (fecha_fin_real.year - item['fecha_inicio'].year) * 12 + (fecha_fin_real.month - item['fecha_inicio'].month)
            total_meses += max(1, diff + 1) 
            total_alumnos += 1

    promedio_meses = total_meses / total_alumnos if total_alumnos > 0 else 0
    promedio_anos = int(promedio_meses // 12)
    promedio_meses_restantes = int(promedio_meses % 12)
    promedio_permanencia_fmt = f"{promedio_anos} Año/s y {promedio_meses_restantes} Meses"

    # ===========================
    #     DATOS A PASAR
    # ===========================
    data_kpis = {
        "kpis": {
            "alumnos_activos": {
                "label": "Total Alumnos Activos", 
                "value": cant_alumnos_activos, 
                "icon": "fa-user-graduate"
            },
            "alumnos_ingresantes": {
                "label": f"Ingresantes {anio_actual}", 
                "value": cant_alumnos_ingresantes, 
                "icon": "fa-user-plus"
            },
            "alumnos_egresados": {
                "label": "Total Egresados", 
                "value": cant_alumnos_egresados, 
                "icon": "fa-medal"
            },
            "tasa_retencion": { 
                "label": "Tasa de Retención",
                "value": tasa_retencion_fmt, 
                "icon": "fa-chart-line"
            },
            "prom_permanencia": { 
                "label": "Promedio de Permanencia",
                "value": promedio_permanencia_fmt, 
                "icon": "fa-clock"
            },
        }
    }
    return data_kpis

#=====================================================
#                       CHARTS
#=====================================================

def get_charts_alumnos():
    anio_actual = timezone.now().year
    anio_inicio = anio_actual - 3
    years = [str(y) for y in range(anio_inicio, anio_actual + 1)]
    
    try:
        id_estado_finalizado = Estado.objects.get(descripcion__iexact='Finalizado').id_estado
    except Estado.DoesNotExist:
        id_estado_finalizado = 4

    # ===========================
    # Egresados vs Ingresantes por Año
    # ===========================

    # --- Ingresantes por Año ---
    ingresantes_por_año = list(
        Alumno.objects.filter(
            anio_ingreso__gte=anio_inicio,
            anio_ingreso__lte=anio_actual
        ).values('anio_ingreso')
        .annotate(count=Count('id_alumno'))
        .order_by('anio_ingreso')
    )
    ingresantes = [next((item['count'] for item in ingresantes_por_año if str(item['anio_ingreso']) == y), 0) for y in years]

    # --- Egresados por Año ---   
    # Año de Finalización = Año del último pago
    egresados_data = CarreraCursada.objects.filter(
        id_estado__id_estado=id_estado_finalizado,
        alumno__pago__fecha_pago__isnull=False
    ).values('alumno_id').annotate(
        anio_finalizacion=Max(ExtractYear('alumno__pago__fecha_pago'))
    ).filter(
        anio_finalizacion__gte=anio_inicio,
        anio_finalizacion__lte=anio_actual
    ).values('anio_finalizacion').annotate(
        count=Count('alumno_id', distinct=True)
    ).order_by('anio_finalizacion')

    egresados = [next((item['count'] for item in egresados_data if str(item['anio_finalizacion']) == y), 0) for y in years]
    
    # ===========================
    #   Distribución por Carrera
    # ===========================
    distribucion_carrera = CarreraCursada.objects.filter(
        id_estado__descripcion__iexact='Activo'
    ).values('carrera__descripcion').annotate(value=Count('alumno', distinct=True)).order_by('-value')
    
    por_carrera = [{"value": item['value'], "name": item['carrera__descripcion']} for item in distribucion_carrera]

    # ===========================
    #   Distribución por Género 
    # ===========================
    distribucion_genero_data = [
        {"value": 15, "name": "Masculino"},
        {"value": 18, "name": "Femenino"}
    ]
    por_genero = distribucion_genero_data
    
    # ===========================
    #   Distribución por Edad
    # ===========================
    
    # Rangos de edad son: 18-22, 23-27, 28-32, +33
    
    today = date.today()
    edades = Alumno.objects.filter(
        fecha_nacimiento__isnull=False
    ).annotate(
        edad=ExtractYear(today) - ExtractYear('fecha_nacimiento')
    ).aggregate(
        r18_22=Count(Case(When(edad__range=(18, 22), then=1), output_field=IntegerField())),
        r23_27=Count(Case(When(edad__range=(23, 27), then=1), output_field=IntegerField())),
        r28_32=Count(Case(When(edad__range=(28, 32), then=1), output_field=IntegerField())),
        r33_mas=Count(Case(When(edad__gte=33, then=1), output_field=IntegerField()))
    )

    distribucion_edad_data = [
        edades['r18_22'], 
        edades['r23_27'], 
        edades['r28_32'], 
        edades['r33_mas']
    ]
    por_edad = distribucion_edad_data

    # ===========================
    # Distribución Geográfica
    # ===========================
    distribucion_geografia = Alumno.objects.values('ciudad').annotate(value=Count('id_alumno')).order_by('-value')
    por_geografia = [{"value": item['value'], "name": item['ciudad']} for item in distribucion_geografia]
    
    
    # ===========================
    #       DATOS A PASAR
    # ===========================
    data_charts = {
        "charts_data": {
            "years": years,
            "ingresantes": ingresantes,
            "egresados": egresados,
            "por_carrera": por_carrera,
            "por_genero": por_genero,
            "por_edad": por_edad,
            "por_geografia": por_geografia,
        }
    }
    
    return data_charts