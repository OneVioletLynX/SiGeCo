import os
import datetime
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render
from reportes.services import get_contabilidad_data, get_alumnos_data, get_admin_data, alumnos_filter_data, bonos_por_carrera_data, bonos_matriz_data
from xhtml2pdf import pisa
from carreras.models import Estado, Carrera
from django.templatetags.static import static


def seccion_contabilidad(request):
    return JsonResponse(get_contabilidad_data())

def seccion_alumnos(request):
    return JsonResponse(get_alumnos_data())

def seccion_admin(request):
    return JsonResponse(get_admin_data())

def generar_pdf_alumnos(request):
    header_url = request.build_absolute_uri(static("header.png"))
    footer_url = request.build_absolute_uri(static("footer.png"))

    # ======== ESTADOS =========
    estados_raw = request.GET.getlist("estado")
    if not estados_raw or estados_raw == ["all"]:
        estados_seleccionados = []
    else:
        estados_plano = ",".join(estados_raw)
        estados_seleccionados = [
            e.strip() for e in estados_plano.split(",") if e.strip().isdigit()
        ]

    # ======== CARRERA =========
    carrera_seleccionada_id = request.GET.get("carrera")
    carrera_descripcion = None
    if carrera_seleccionada_id in [None, "", "all"]:
        carrera_seleccionada_id = None
    elif carrera_seleccionada_id.isdigit():
        try:
            carrera_obj = Carrera.objects.get(id_carrera=carrera_seleccionada_id)
            carrera_descripcion = carrera_obj.descripcion
        except Carrera.DoesNotExist:
            carrera_seleccionada_id = None

    filtros = {
        "estado": estados_seleccionados,
        "carrera": carrera_seleccionada_id, 
    }

    data_alumnos_filtrados = alumnos_filter_data(filtros)

    # ======== TÍTULO =========
    titulo_adicional = ""

    # Estados
    if estados_seleccionados:
        estado_descripciones = Estado.objects.filter(
            id_estado__in=estados_seleccionados
        ).values_list('descripcion', flat=True)

        if len(estado_descripciones) == 1:
            titulo_adicional += f" | Estado: {estado_descripciones[0]}"
        else:
            titulo_adicional += f" | Estados: {', '.join(estado_descripciones)}"
    # Carreras
    if carrera_descripcion:
        titulo_adicional += f" | Carrera: {carrera_descripcion}"

    contexto = {
        'titulo_reporte': 'Listado de Alumnos' + titulo_adicional,
        'fecha_generacion': datetime.date.today().strftime('%d/%m/%Y'),
        'data_alumnos': data_alumnos_filtrados,
        "header_url": header_url,
        "footer_url": footer_url,
    }

    html_string = render_to_string('reportes/reportes_alumnos_pdf.html', contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Listado_de_alumnos.pdf"' 
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse('<h1>Error al generar el PDF</h1>' + html_string, status=500)

    return response

def bonos_matriz_view(request):
    carrera_id = request.GET.get('carrera')
    anio_raw   = request.GET.get('anio')
    ingresantes = request.GET.get('ingresantes', 'true').lower() == 'true'

    if not carrera_id or not str(carrera_id).isdigit():
        return JsonResponse({'error': 'Carrera requerida'}, status=400)

    try:
        anio = int(anio_raw)
    except (ValueError, TypeError):
        anio = datetime.date.today().year

    data = bonos_matriz_data(int(carrera_id), anio, ingresantes)
    return JsonResponse(data)

def preview_bonos_por_carrera(request):
    fecha_desde_raw = request.GET.get("fecha_desde")
    fecha_hasta_raw = request.GET.get("fecha_hasta")

    today = datetime.date.today()
    try:
        fecha_desde = datetime.datetime.strptime(fecha_desde_raw, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha_desde = today.replace(month=1, day=1)

    try:
        fecha_hasta = datetime.datetime.strptime(fecha_hasta_raw, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha_hasta = today

    data = bonos_por_carrera_data(fecha_desde, fecha_hasta)
    return JsonResponse(data, safe=False)

def generar_pdf_bonos_por_carrera(request):
    header_url = request.build_absolute_uri(static("header.png"))
    footer_url = request.build_absolute_uri(static("footer.png"))

    # ======== FILTROS DE FECHA =========
    fecha_desde_raw = request.GET.get("fecha_desde")
    fecha_hasta_raw = request.GET.get("fecha_hasta")

    today = datetime.date.today()
    try:
        fecha_desde = datetime.datetime.strptime(fecha_desde_raw, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha_desde = today.replace(day=1).replace(month=1)

    try:
        fecha_hasta = datetime.datetime.strptime(fecha_hasta_raw, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        fecha_hasta = today

    # Obtener los datos del servicio
    data_bonos_por_carrera = bonos_por_carrera_data(fecha_desde, fecha_hasta)
    
    # Calcular totales
    total_general_bonos_count = sum(item['bonos_cobrados'] for item in data_bonos_por_carrera)
    total_general_cobrado_sum = sum(item['total_cobrado'] for item in data_bonos_por_carrera)

    contexto = {
        'titulo_reporte': 'Bonos Cooperadores Cobrados por Carrera',
        'fecha_desde': fecha_desde.strftime('%d/%m/%Y'),
        'fecha_hasta': fecha_hasta.strftime('%d/%m/%Y'),
        'fecha_informe': today.strftime('%d/%m/%Y'),
        'data_reporte': data_bonos_por_carrera,
        'total_general_bonos': total_general_bonos_count,
        'total_general_cobrado': total_general_cobrado_sum,
        "header_url": header_url,
        "footer_url": footer_url,
    }

    html_string = render_to_string('reportes/reportes_bonos_PDF.html', contexto)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bonos_por_carrera.pdf"' 
    pisa_status = pisa.CreatePDF(html_string, dest=response)

    if pisa_status.err:
        return HttpResponse('<h1>Error al generar el PDF de bonos</h1>' + html_string, status=500)

    return response