from datetime import date
from django.db.models import Count, Max, Min, Case, When, IntegerField, ExpressionWrapper
from alumnos.models import Alumno
from carreras.models import CarreraCursada, Carrera, Estado
from django.db.models.functions import ExtractYear
from ctacte.models import Pago, PagoDetalle, MesPago
from django.utils import timezone


# =====================================================
#                       KPIS
# =====================================================

def get_kpis_alumnos():
    ID_ACTIVO     = 1
    ID_FINALIZADO = 4
    anio_actual   = timezone.now().year

    # --- Alumnos activos ---
    alumnos_activos_ids = CarreraCursada.objects.filter(
        id_estado__id_estado=ID_ACTIVO
    ).values_list('alumno_id', flat=True).distinct()
    cant_alumnos_activos = alumnos_activos_ids.count()

    # --- Egresados ---
    try:
        id_estado_egresado = Estado.objects.get(descripcion__iexact='Finalizado').id_estado
    except Estado.DoesNotExist:
        id_estado_egresado = ID_FINALIZADO

    cant_alumnos_egresados = CarreraCursada.objects.filter(
        id_estado__id_estado=id_estado_egresado
    ).values('alumno_id').distinct().count()

    # --- Ingresantes (campo anio_ingreso no disponible en el modelo) ---
    cant_alumnos_ingresantes = 0

    # --- Tasa de retención ---
    cant_total = Alumno.objects.count()
    tasa_retencion = (cant_alumnos_activos / cant_total * 100) if cant_total > 0 else 0
    tasa_retencion_fmt = f"{tasa_retencion:.1f}%"

    # --- Promedio años de permanencia ---
    permanencia_data = Alumno.objects.filter(
        pagos__fecha_pago__isnull=False
    ).annotate(
        fecha_inicio=Min('pagos__fecha_pago'),
        fecha_fin=Max('pagos__fecha_pago'),
    ).distinct().values('fecha_inicio', 'fecha_fin', 'id_alumno')

    total_meses  = 0
    total_alumnos = 0
    for item in permanencia_data:
        if item['fecha_inicio'] and item['fecha_fin']:
            diff = (
                (item['fecha_fin'].year  - item['fecha_inicio'].year)  * 12
              + (item['fecha_fin'].month - item['fecha_inicio'].month)
            )
            total_meses   += max(1, diff + 1)
            total_alumnos += 1

    promedio_meses           = total_meses / total_alumnos if total_alumnos > 0 else 0
    promedio_anos            = int(promedio_meses // 12)
    promedio_meses_restantes = int(promedio_meses % 12)
    promedio_permanencia_fmt = f"{promedio_anos} año/s y {promedio_meses_restantes} meses"

    return {
        "kpis": {
            "alumnos_activos":     {"label": "Total alumnos activos",    "value": cant_alumnos_activos},
            "alumnos_ingresantes": {"label": f"Ingresantes {anio_actual}", "value": cant_alumnos_ingresantes},
            "alumnos_egresados":   {"label": "Total egresados",           "value": cant_alumnos_egresados},
            "tasa_retencion":      {"label": "Tasa de retención",         "value": tasa_retencion_fmt},
            "prom_permanencia":    {"label": "Promedio de permanencia",   "value": promedio_permanencia_fmt},
        }
    }


# =====================================================
#                       CHARTS
# =====================================================

def get_charts_alumnos():
    anio_actual = timezone.now().year
    anio_inicio = anio_actual - 3
    years       = [str(y) for y in range(anio_inicio, anio_actual + 1)]

    try:
        id_estado_finalizado = Estado.objects.get(descripcion__iexact='Finalizado').id_estado
    except Estado.DoesNotExist:
        id_estado_finalizado = 4

    # --- Ingresantes por año (sin campo anio_ingreso → ceros) ---
    ingresantes = [0] * len(years)

    # --- Egresados por año ---
    egresados_data = (
        CarreraCursada.objects
        .filter(
            id_estado__id_estado=id_estado_finalizado,
            alumno__pagos__fecha_pago__isnull=False,
        )
        .values('alumno_id')
        .annotate(anio_finalizacion=Max(ExtractYear('alumno__pagos__fecha_pago')))
        .filter(anio_finalizacion__gte=anio_inicio, anio_finalizacion__lte=anio_actual)
        .values('anio_finalizacion')
        .annotate(count=Count('alumno_id', distinct=True))
        .order_by('anio_finalizacion')
    )
    egresados = [
        next((item['count'] for item in egresados_data if str(item['anio_finalizacion']) == y), 0)
        for y in years
    ]

    # --- Distribución por carrera ---
    distribucion_carrera = (
        CarreraCursada.objects
        .filter(id_estado__descripcion__iexact='Activo')
        .values('carrera__descripcion')
        .annotate(value=Count('alumno', distinct=True))
        .order_by('-value')
    )
    por_carrera = [{"value": item['value'], "name": item['carrera__descripcion']} for item in distribucion_carrera]

    # --- Distribución por género (sin campo en el modelo) ---
    por_genero = [{"value": 1, "name": "Sin datos"}]

    # --- Distribución por edad (FIX: usar today_year como entero) ---
    today_year = date.today().year
    try:
        edades = (
            Alumno.objects
            .filter(fecha_nacimiento__isnull=False)
            .annotate(
                edad=ExpressionWrapper(
                    today_year - ExtractYear('fecha_nacimiento'),
                    output_field=IntegerField(),
                )
            )
            .aggregate(
                r18_22 =Count(Case(When(edad__range=(18, 22), then=1), output_field=IntegerField())),
                r23_27 =Count(Case(When(edad__range=(23, 27), then=1), output_field=IntegerField())),
                r28_32 =Count(Case(When(edad__range=(28, 32), then=1), output_field=IntegerField())),
                r33_mas=Count(Case(When(edad__gte=33,          then=1), output_field=IntegerField())),
            )
        )
        por_edad = [edades['r18_22'], edades['r23_27'], edades['r28_32'], edades['r33_mas']]
    except Exception:
        por_edad = [0, 0, 0, 0]

    # --- Distribución geográfica (FIX: ciudad es FK → ciudad__nombre) ---
    try:
        distribucion_geografia = (
            Alumno.objects
            .values('ciudad__nombre')
            .annotate(value=Count('id_alumno'))
            .order_by('-value')[:10]
        )
        por_geografia = [
            {"value": item['value'], "name": item['ciudad__nombre']}
            for item in distribucion_geografia
        ]
    except Exception:
        por_geografia = []

    return {
        "charts_data": {
            "years":         years,
            "ingresantes":   ingresantes,
            "egresados":     egresados,
            "por_carrera":   por_carrera,
            "por_genero":    por_genero,
            "por_edad":      por_edad,
            "por_geografia": por_geografia,
        }
    }
