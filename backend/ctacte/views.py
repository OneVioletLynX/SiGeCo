from datetime import date
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.utils import timezone

from alumnos.models import Alumno
from carreras.models import CarreraCursada
from .models import MesPago, MetodoPago, Pago, PagoDetalle, Cuota
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
        pagos = Pago.objects.all().order_by('-fecha_pago', '-id_pago')
        alumno_id = request.query_params.get('alumno')
        if alumno_id:
            pagos = pagos.filter(id_alumno_id=alumno_id)
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

        return Response(
            PagoReadSerializer(pago).data,
            status=status.HTTP_201_CREATED
        )


# -------- MesesPendientes --------
#
# GET /ctacte/pendientes/?alumno=<id>

class MesesPendientes(APIView):

    def get(self, request):
        alumno_id = request.query_params.get("alumno")

        if not alumno_id:
            return Response({"error": "Falta el parámetro 'alumno'."}, status=400)

        alumno = get_object_or_404(Alumno, pk=alumno_id)

        cuotas = (
            Cuota.objects
            .filter(alumno=alumno)
            .select_related("mes", "carrera", "estado")
            .order_by("anio", "mes_id")
        )

        ultima_pagada = (
            cuotas
            .filter(estado__descripcion__iexact="pagada")
            .order_by("-anio", "-mes_id")
            .first()
        )
        ultimo_pagado = (
            {"mes": ultima_pagada.mes_id, "anio": ultima_pagada.anio}
            if ultima_pagada else None
        )

        # Armar dict (carrera_id, mes_id, anio) → id_pago para cuotas pagadas
        pagos_del_alumno = (
            PagoDetalle.objects
            .filter(pago__id_alumno=alumno)
            .values("carrera_id", "mes_id", "anio_pago", "pago__id_pago")
        )
        pago_lookup = {
            (p["carrera_id"], p["mes_id"], p["anio_pago"]): p["pago__id_pago"]
            for p in pagos_del_alumno
        }

        meses_por_anio = {}
        for cuota in cuotas:
            anio = str(cuota.anio)
            if anio not in meses_por_anio:
                meses_por_anio[anio] = []

            estado    = cuota.estado.descripcion.lower()
            es_pagada = estado == "pagada"
            id_pago   = pago_lookup.get((cuota.carrera_id, cuota.mes_id, cuota.anio)) if es_pagada else None

            meses_por_anio[anio].append({
                "id_cuota":       cuota.id_cuota,
                "id_mes":         cuota.mes_id,
                "descripcion":    cuota.mes.descripcion,
                "carrera":        cuota.carrera_id,
                "carrera_nombre": cuota.carrera.descripcion,
                "estado":         estado,
                "pagado":         es_pagada,
                "id_pago":        id_pago,
                "importe":        cuota.importe,
            })

        return Response({
            "alumno":        alumno.id_alumno,
            "anio_ingreso":  cuotas.first().anio if cuotas.exists() else None,
            "anio_final":    cuotas.last().anio  if cuotas.exists() else None,
            "ultimo_pagado": ultimo_pagado,
            "meses":         meses_por_anio,
        })