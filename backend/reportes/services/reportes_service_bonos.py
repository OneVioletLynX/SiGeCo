import datetime
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import Coalesce

# Importaciones necesarias
from carreras.models import Carrera 
from ctacte.models import PagoDetalle
from valores.models import Concepto, Valor 


def bonos_por_carrera_data(fecha_desde, fecha_hasta):
    # 1. IDENTIFICAR CONCEPTOS CLAVE
    CONCEPTO_CUOTA_ID = 1 
    CONCEPTO_INSCRIPCION_ID = 2
    
    # 2. OBTENER VALORES BASE DE LA CUOTA POR CARRERA
    valor_cuota_por_carrera = {}
    for carrera in Carrera.objects.all():
        # Consulta para Valor sigue usando la relación normal de Django: id_concepto__id_concepto
        valor_obj = Valor.objects.filter(
            id_carrera=carrera,
            id_concepto__id_concepto=CONCEPTO_CUOTA_ID,
            fecha_inicio__lte=fecha_hasta 
        ).order_by('-fecha_inicio').first()
        
        valor_cuota_por_carrera[carrera.id_carrera] = float(valor_obj.importe) if valor_obj else 0.00
    
    
    # 3. CONSOLIDAR RESULTADOS POR CARRERA
    
    # Pre-cargar solo las relaciones de carrera y alumno necesarias
    carreras_existentes = Carrera.objects.all().order_by('descripcion').prefetch_related(
        'carreras_cursadas__alumno'
    )
    final_report = []

    for carrera in carreras_existentes:
        carrera_desc = carrera.descripcion
        carrera_id = carrera.id_carrera
        
        # Obtenemos los IDs de los alumnos activos de esta carrera
        alumnos_de_la_carrera = carrera.carreras_cursadas.filter(id_estado__pk=1).values_list('alumno_id', flat=True)
        
        # 🟢 CORRECCIÓN: Evitamos select_related y uniones complejas
        # El queryset base solo filtra por pago y alumno
        detalles_carrera_en_rango = PagoDetalle.objects.filter(
            pago__fecha_pago__date__range=[fecha_desde, fecha_hasta],
            pago__id_alumno_id__in=alumnos_de_la_carrera
        )
        
        valor_base_cuota = valor_cuota_por_carrera.get(carrera_id, 0.00)

        # --- A. CÁLCULO de CUOTAS/BONOS y VENCIDOS ---
        
        # ✅ USAMOS id_concepto DIRECTAMENTE (Asumimos que la columna en la BD es 'id_concepto')
        cuotas_qs = detalles_carrera_en_rango.filter(id_concepto=CONCEPTO_CUOTA_ID)
        
        bonos_cobrados_count = cuotas_qs.count()
        monto_cuotas_pagadas = cuotas_qs.aggregate(sum_importe=Coalesce(Sum('importe'), 0.00))['sum_importe']
        
        # Monto de Vencidos/Recargos = Monto pagado - (Valor Base * Cantidad)
        monto_base_teorico = valor_base_cuota * bonos_cobrados_count
        monto_vencidos = max(0.00, monto_cuotas_pagadas - monto_base_teorico)


        # --- B. CÁLCULO de INSCRIPCIONES ---
        
        # ✅ USAMOS id_concepto DIRECTAMENTE
        inscripciones_qs = detalles_carrera_en_rango.filter(id_concepto=CONCEPTO_INSCRIPCION_ID)
        monto_inscripciones = inscripciones_qs.aggregate(sum_importe=Coalesce(Sum('importe'), 0.00))['sum_importe']
        

        # --- C. TOTALIZACIÓN ---
        
        total_cobrado_carrera = monto_cuotas_pagadas + monto_inscripciones
        
        final_report.append({
            'carrera': carrera_desc,
            'bonos_cobrados': bonos_cobrados_count,
            'monto_bonos_total': monto_cuotas_pagadas,
            'vencidos': monto_vencidos,             
            'inscripciones': monto_inscripciones,    
            'total_cobrado': total_cobrado_carrera,
        })
        
    return final_report