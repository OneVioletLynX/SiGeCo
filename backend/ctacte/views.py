from datetime import date
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from backend.permissions import TienePermisoRol
from datetime import date as fecha_hoy


from alumnos.models import Alumno
from carreras.models import CarreraCursada
from .models import MesPago, MetodoPago, Pago, PagoDetalle, Cuota
from auditoria.models import registrar
from .serializers import (
    MesPagoSerializer,
    MetodoPagoSerializer,
    PagoReadSerializer,
    PagoWriteSerializer,
    PagoDetalleSerializer,
    PagoDetalleLiteSerializer,
)
from .services import MESES_CICLO, MESES_CALENDARIO


# --- FRONTEND ---

def home_ctacte(request):
    return render(request, "ctacte/home.html")


# --- API ROOT ---

@api_view(['GET'])
def ctacte_api_root(request):
    return Response({
        'meses':          request.build_absolute_uri(reverse('ctacte:mespago-list')),
        'metodos-pagos':  request.build_absolute_uri(reverse('ctacte:metodopago-list')),
        'pagos':          request.build_absolute_uri(reverse('ctacte:pago-list')),
        'pagos-detalle':  request.build_absolute_uri(reverse('ctacte:pagodetalle-list')),
        'registrar-pago': request.build_absolute_uri(reverse('ctacte:registrar-pago')),
        'pendientes':     request.build_absolute_uri(reverse('ctacte:ctacte-pendientes')),
    })


# -------- MesPago --------

class MesPagoListCreate(APIView):
    def get(self, request):
        objs = MesPago.objects.all().order_by('id_mes')
        return Response(MesPagoSerializer(objs, many=True).data)

    def post(self, request):
        ser = MesPagoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class MesPagoDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(MesPago, pk=pk)
        return Response(MesPagoSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(MesPago, pk=pk)
        ser = MesPagoSerializer(obj, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(MesPago, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------- MetodoPago --------

class MetodoPagoListCreate(APIView):
    def get(self, request):
        objs = MetodoPago.objects.all().order_by('id_metodo_pago')
        return Response(MetodoPagoSerializer(objs, many=True).data)

    def post(self, request):
        ser = MetodoPagoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class MetodoPagoDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(MetodoPago, pk=pk)
        return Response(MetodoPagoSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(MetodoPago, pk=pk)
        ser = MetodoPagoSerializer(obj, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(MetodoPago, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------- Pago --------

class PagoListCreate(APIView):
    def get(self, request):
            pagos = Pago.objects.all().select_related(
                "id_alumno", "id_metodo_pago"
            ).prefetch_related(
                "detalles__carrera", "detalles__mes"
            ).order_by('-fecha_pago', '-id_pago')
    
            alumno_id  = request.query_params.get('alumno')
            metodo_id  = request.query_params.get('metodo')
            carrera_id = request.query_params.get('carrera')
            limit      = int(request.query_params.get('limit', 20))
    
            if alumno_id:
                pagos = pagos.filter(id_alumno_id=alumno_id)
            if metodo_id:
                pagos = pagos.filter(id_metodo_pago_id=metodo_id)
            if carrera_id:
                pagos = pagos.filter(detalles__carrera_id=carrera_id).distinct()
    
            pagos = pagos[:limit]
            return Response(PagoReadSerializer(pagos, many=True).data)

    def post(self, request):
        ser = PagoWriteSerializer(data=request.data)
        if ser.is_valid():
            pago = ser.save()
            return Response(PagoReadSerializer(pago).data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)
        return Response(PagoReadSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)
        ser = PagoWriteSerializer(obj, data=request.data)
        if ser.is_valid():
            pago = ser.save()
            return Response(PagoReadSerializer(pago).data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)

        # Antes de eliminar el pago, revertir las cuotas asociadas a "Pendiente"
        detalles = PagoDetalle.objects.filter(pago=obj)
        for det in detalles:
            Cuota.objects.filter(
                alumno=obj.id_alumno,
                carrera=det.carrera,
                mes=det.mes,
                anio=det.anio_pago,
            ).update(estado_id=2)  # 2 = "Pendiente"

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------- PagoDetalle --------

class PagoDetalleListCreate(APIView):
    def get(self, request):
        objs = PagoDetalle.objects.all().order_by('id_detalle')
        return Response(PagoDetalleLiteSerializer(objs, many=True).data)

    def post(self, request):
        ser = PagoDetalleSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoDetalleDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(PagoDetalle, pk=pk)
        return Response(PagoDetalleLiteSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(PagoDetalle, pk=pk)
        ser = PagoDetalleSerializer(obj, data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(PagoDetalle, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------- RegistrarPago --------
#
# Body esperado:
# {
#     "id_alumno": 1,
#     "id_metodo_pago": 2,
#     "meses": [
#         {"carrera": 1, "mes": 1,  "anio": 2026, "concepto": 1, "importe": 50000},  <- Inscripcion
#         {"carrera": 1, "mes": 3,  "anio": 2026, "concepto": 1, "importe": 40000},  <- Marzo
#         {"carrera": 1, "mes": 4,  "anio": 2026, "concepto": 1, "importe": 40000},  <- Abril
#     ]
# }

class RegistrarPago(APIView):

    @transaction.atomic
    def post(self, request):
        data       = request.data
        alumno_id  = data.get("id_alumno")
        metodo_id  = data.get("id_metodo_pago")
        meses_data = data.get("meses", [])

        if not alumno_id or not metodo_id or not meses_data:
            return Response(
                {"error": "Faltan datos obligatorios: id_alumno, id_metodo_pago y meses."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            alumno = Alumno.objects.get(pk=alumno_id)
        except Alumno.DoesNotExist:
            return Response({"error": f"No existe el alumno con id {alumno_id}."}, status=404)

        try:
            metodo = MetodoPago.objects.get(pk=metodo_id)
        except MetodoPago.DoesNotExist:
            return Response({"error": f"No existe el método de pago con id {metodo_id}."}, status=404)

        hoy = date.today()

        # Validaciones previas por cada ítem (antes de tocar la BD)
        for item in meses_data:
            mes_num    = item.get("mes")
            anio       = item.get("anio")
            carrera_id = item.get("carrera")

            # REGLA: solo meses del ciclo académico (Inscripcion + Marzo-Diciembre)
            if mes_num not in MESES_CICLO:
                return Response(
                    {"error": f"El mes {mes_num} no es válido. Valores permitidos: {sorted(MESES_CICLO)}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # REGLA: no se pueden pagar meses futuros.
            # Inscripcion (id=1) no es un mes calendario, no aplica esta validación.
            if mes_num in MESES_CALENDARIO:
                if anio > hoy.year or (anio == hoy.year and mes_num > hoy.month):
                    return Response(
                        {"error": f"No se pueden pagar meses futuros (mes={mes_num}, año={anio})."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # REGLA: un alumno no puede pagar el mismo mes/carrera/año dos veces
            ya_pago = PagoDetalle.objects.filter(
                pago__id_alumno=alumno,
                carrera_id=carrera_id,
                mes_id=mes_num,
                anio_pago=anio,
            ).exists()

            if ya_pago:
                return Response(
                    {"error": f"El alumno ya pagó carrera={carrera_id}, mes={mes_num}, año={anio}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calcular importe total
        try:
            importe_total = sum(float(item["importe"]) for item in meses_data)
        except (KeyError, TypeError, ValueError):
            return Response(
                {"error": "Cada ítem de 'meses' debe tener 'importe' numérico."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear cabecera del pago
        pago = Pago.objects.create(
            id_alumno=alumno,
            id_metodo_pago=metodo,
            fecha_pago=timezone.now(),
            importe_total=importe_total,
        )

        # Crear detalles y marcar cuotas como pagadas
        for item in meses_data:
            try:
                mes_obj = MesPago.objects.get(pk=item["mes"])
            except MesPago.DoesNotExist:
                return Response(
                    {"error": f"No existe el mes con id {item['mes']}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            PagoDetalle.objects.create(
                pago=pago,
                carrera_id=item["carrera"],
                mes=mes_obj,
                anio_pago=item["anio"],
                id_concepto_id=item.get("concepto"),
                importe=item["importe"],
            )

            # Marcar la cuota correspondiente como pagada.
            # REGLA: el pago parcial igual deja el mes como pagado.
            Cuota.objects.filter(
                alumno=alumno,
                carrera_id=item["carrera"],
                mes=mes_obj,
                anio=item["anio"],
            ).update(estado_id=1)  # 1 = "Pagada"

        registrar(
            request, 'COBRO', 'cobro',
            f"Cobro ${importe_total:,.0f} — {alumno.apellido}, {alumno.nombre}",
            pago.id_pago,
        )
        return Response(
            PagoReadSerializer(pago).data,
            status=status.HTTP_201_CREATED
        )


# -------- MesesPendientes --------
#
# GET /ctacte/pendientes/?alumno=<id>

class MesesPendientes(APIView):
    """
    GET /ctacte/pendientes/?alumno=ID
    Devuelve todas las cuotas del alumno agrupadas por año,
    con el campo carrera, estado correcto, id_pago y ultimo_pagado.
    """

    def get(self, request):

        alumno_id = request.query_params.get("alumno")
        if not alumno_id:
            return Response({"error": "Falta el parámetro alumno"}, status=400)

        alumno = get_object_or_404(Alumno, pk=alumno_id)

        cuotas = (
            Cuota.objects
            .filter(alumno=alumno)
            .select_related("mes", "carrera", "estado")
            .order_by("anio", "mes_id")
        )

        # Mapear cuota → id_pago buscando en PagoDetalle
        # Buscar pagos del alumno y sus detalles
        pago_por_cuota = {}
        pagos_alumno = Pago.objects.filter(id_alumno=alumno).values_list("id_pago", flat=True)
        detalles = PagoDetalle.objects.filter(
            pago__in=pagos_alumno
        ).select_related("pago")
        for detalle in detalles:
            clave = (detalle.carrera_id, detalle.mes_id, detalle.anio_pago)
            pago_por_cuota[clave] = detalle.pago.id_pago

        meses_por_anio = {}
        ultimo_pagado  = None

        for cuota in cuotas:
            anio   = str(cuota.anio)
            estado = cuota.estado.descripcion.lower()  # "pagada" o "pendiente"
            id_pago = pago_por_cuota.get((cuota.carrera_id, cuota.mes_id, cuota.anio))

            if anio not in meses_por_anio:
                meses_por_anio[anio] = []

            meses_por_anio[anio].append({
                "id_mes":      cuota.mes_id,
                "descripcion": cuota.mes.descripcion,
                "carrera":     cuota.carrera.id_carrera,
                "estado":      estado,
                "pagado":      estado == "pagada",
                "id_pago":     id_pago,
            })

            # Rastrear el último mes pagado para calcular bloqueos
            if estado == "pagada":
                ultimo_pagado = {
                    "mes":  cuota.mes_id,
                    "anio": cuota.anio,
                }

        # Año de ingreso: el año de la cuota de inscripcion (mes_id=1)
        cuota_inscripcion = cuotas.filter(mes_id=1).first()
        anio_ingreso = cuota_inscripcion.anio if cuota_inscripcion else (cuotas.first().anio if cuotas else None)

        return Response({
            "alumno":        alumno.id_alumno,
            "anio_ingreso":  anio_ingreso,
            "ultimo_pagado": ultimo_pagado,
            "meses":         meses_por_anio,
        })

class GenerarCuotasMes(APIView):
    """
    POST /ctacte/generar-cuotas/
    Genera las cuotas del mes actual para todos los alumnos activos.
    Solo accesible para ADMIN y SECRETARIA.
    """

    def post(self, request):
        from .services import generar_cuotas_mes
        from datetime import date

        hoy    = date.today()
        resultado = generar_cuotas_mes(anio=hoy.year, mes=hoy.month)

        if "motivo" in resultado:
            return Response({"warning": resultado["motivo"]}, status=200)

        return Response({
            "generadas": resultado["generadas"],
            "mes":       hoy.month,
            "anio":      hoy.year,
        }, status=200)


class ResumenMesActual(APIView):
    """
    GET /ctacte/resumen-mes/
    Devuelve un resumen del estado de las cuotas del mes actual.
    """

    def get(self, request):
        from .models import Cuota, MesPago, EstadoCuota
        from datetime import date

        hoy    = date.today()
        mes_id = hoy.month
        anio   = hoy.year

        mes_obj = MesPago.objects.filter(id_mes=mes_id).first()

        cuotas_total    = Cuota.objects.filter(mes=mes_obj, anio=anio).count()         if mes_obj else 0
        cuotas_pagadas  = Cuota.objects.filter(mes=mes_obj, anio=anio, estado__descripcion__iexact="pagada").count()  if mes_obj else 0
        cuotas_pendientes = cuotas_total - cuotas_pagadas

        ya_generadas = cuotas_total > 0

        return Response({
            "mes":              mes_obj.descripcion if mes_obj else "—",
            "mes_id":           mes_id,
            "anio":             anio,
            "ya_generadas":     ya_generadas,
            "cuotas_total":     cuotas_total,
            "cuotas_pagadas":   cuotas_pagadas,
            "cuotas_pendientes": cuotas_pendientes,
        })