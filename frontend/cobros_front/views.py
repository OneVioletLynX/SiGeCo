from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
import io
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from pypdf import PdfReader, PdfWriter

from backend.ctacte.models import Pago, PagoDetalle, MesPago, MetodoPago


def listado_cobros(request):
    """Listado de cobros con filtros."""
    return render(request, 'cobros/cobros_listado.html')


def cobros(request):
    """Pantalla de registrar cobro."""
    meses   = MesPago.objects.all().order_by('id_mes')
    metodos = MetodoPago.objects.all().order_by('id_metodo_pago')
    return render(request, 'cobros/index.html', {'meses': meses, 'metodos': metodos})


def comprobante_cobro_pdf(request, id_pago):
    pago     = get_object_or_404(Pago, id_pago=id_pago)
    detalles = PagoDetalle.objects.filter(pago=pago).select_related("mes", "carrera")
    alumno   = pago.id_alumno

    carrera_nombre = ""
    anio_ingreso   = ""

    primer_detalle = detalles.first()
    if primer_detalle:
        cc = alumno.carreras_cursadas.filter(
            carrera=primer_detalle.carrera
        ).select_related("carrera").first()
    else:
        cc = alumno.carreras_cursadas.select_related("carrera").first()

    if cc:
        carrera_nombre = cc.carrera.descripcion
        anio_ingreso   = cc.anio_ingreso

    packet = io.BytesIO()
    can    = canvas.Canvas(packet, pagesize=landscape(A4))

    def write(x, y, text):
        can.drawString(x, y, str(text))

    columnas_x = [65, 335, 605]
    y_fecha   = 450
    y_nombre  = 432
    y_estado  = 414
    y_carrera = 385
    y_anio    = 366
    y_tabla   = 300
    salto_fila = 22
    y_total   = 45

    for x_base in columnas_x:
        write(x_base, y_fecha,   pago.fecha_pago.strftime("%d/%m/%Y %H:%M") if pago.fecha_pago else "")
        write(x_base, y_nombre,  f"{alumno.apellido.upper()} {alumno.nombre.upper()}")
        write(x_base, y_estado,  "Activo")
        write(x_base, y_carrera, carrera_nombre)
        write(x_base, y_anio,    anio_ingreso)

        y = y_tabla
        for det in detalles:
            write(x_base - 40,  y, det.mes.descripcion)
            write(x_base + 30,  y, "Cuota")
            write(x_base + 130, y, f"${det.importe}")
            y -= salto_fila

        write(x_base + 130, y_total, f"${pago.importe_total}")

    can.save()
    packet.seek(0)

    plantilla_path = os.path.join(
        settings.BASE_DIR,
        "shared", "static", "shared", "pdf", "plantilla.pdf"
    )

    template_pdf = PdfReader(open(plantilla_path, "rb"))
    overlay_pdf  = PdfReader(packet)

    writer = PdfWriter()
    page   = template_pdf.pages[0]
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    response = HttpResponse(output, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename=comprobante_{id_pago}.pdf'
    return response