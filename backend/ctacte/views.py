from datetime import date
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Modelos
from alumnos.models import Alumno
from django.utils import timezone
from .models import MesPago, MetodoPago, Pago, PagoDetalle

# Serializers
from .serializers import (
    MesPagoSerializer, MetodoPagoSerializer, PagoSerializer, PagoDetalleSerializer
)

# --- VISTAS DEL FRONTEND ---

def home_ctacte(request):
    return render(request, "ctacte/home.html")

# --- VISTAS DE LA API ---

@api_view(['GET'])
def ctacte_api_root(request):
    return Response({
        'meses': request.build_absolute_uri(reverse('ctacte:mespago-list')),
        'metodos-pagos': request.build_absolute_uri(reverse('ctacte:metodopago-list')),
        'pagos': request.build_absolute_uri(reverse('ctacte:pago-list')),
        'pagos-detalle': request.build_absolute_uri(reverse('ctacte:pagodetalle-list')),
    })


# -------- MesPago --------
class MesPagoListCreate(APIView):
    def get(self, request):
        objs = MesPago.objects.all().order_by('id_mes')
        ser = MesPagoSerializer(objs, many=True)
        return Response(ser.data)

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
        ser = MetodoPagoSerializer(objs, many=True)
        return Response(ser.data)

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
        alumno_id = request.query_params.get('alumno')
        pagos = Pago.objects.all().order_by('-fecha_pago', '-id_pago')
        if alumno_id:
            pagos = pagos.filter(id_alumno_id=alumno_id)

        ser = PagoSerializer(pagos, many=True)
        return Response(ser.data)

    def post(self, request):
        ser = PagoSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)
        return Response(PagoSerializer(obj).data)

    def put(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)
        ser = PagoSerializer(obj, data=request.data, context={'request': request})
        if ser.is_valid():
            ser.save()
            return Response(ser.data)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = get_object_or_404(Pago, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -------- PagoDetalle --------
class PagoDetalleListCreate(APIView):
    def get(self, request):
        objs = PagoDetalle.objects.all().order_by('id_detalle')
        ser = PagoDetalleSerializer(objs, many=True)
        return Response(ser.data)

    def post(self, request):
        ser = PagoDetalleSerializer(data=request.data)
        if ser.is_valid():
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)
        return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoDetalleDetail(APIView):
    def get(self, request, pk):
        obj = get_object_or_404(PagoDetalle, pk=pk)
        return Response(PagoDetalleSerializer(obj).data)

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
    
class RegistrarPago(APIView):

    def post(self, request):

        data = request.data

        alumno_id = data.get("id_alumno")
        metodo_id = data.get("id_metodo_pago")
        meses_data = data.get("meses", [])

        if not alumno_id or not metodo_id or not meses_data:
            return Response({"error": "Faltan datos obligatorios"}, status=400)

        alumno = Alumno.objects.get(pk=alumno_id)
        metodo = MetodoPago.objects.get(pk=metodo_id)

        pago = Pago.objects.create(
            id_alumno=alumno,
            id_metodo_pago=metodo,
            fecha_pago=timezone.now(),
            importe_total=data.get("importe_total")
        )

        for item in meses_data:

            mes = MesPago.objects.get(pk=item["mes"])

            PagoDetalle.objects.create(
                pago=pago,
                carrera_id=item["carrera"],
                mes=mes,
                anio_pago=item["anio"],
                id_concepto_id=item.get("concepto", 1),
                importe=item["importe"]
            )

        return Response({
            "success": True,
            "id_pago": pago.id_pago
        }, status=201)


class MesesPendientes(APIView):

    def get(self, request):
        alumno_id = request.query_params.get("alumno")
        if not alumno_id:
            return Response({"error": "Falta el parámetro alumno"}, status=400)

        alumno = get_object_or_404(Alumno, pk=alumno_id)

        # 1️⃣ Año de ingreso
        anio_ingreso = alumno.anio_ingreso or alumno.inscripcion.year

        # 2️⃣ Último detalle pagado (año + mes)
        ultimo_detalle = (
            PagoDetalle.objects
            .filter(
                pago__id_alumno_id=alumno.id_alumno,
                mes__isnull=False
            )
            .exclude(anio_pago__isnull=True)
            .order_by("-anio_pago", "-mes_id")
            .first()
        )

        ultimo_pagado = None
        if ultimo_detalle:
            ultimo_pagado = {
                "anio": ultimo_detalle.anio_pago,
                "mes": ultimo_detalle.mes_id
            }
            anio_final = max(anio_ingreso, ultimo_detalle.anio_pago + 1)
        else:
            anio_final = anio_ingreso + 1

        # 3️⃣ Catálogo de meses
        meses_catalogo = list(
            MesPago.objects
            .exclude(descripcion__icontains="insc")
            .order_by("id_mes")
            .values("id_mes", "descripcion")
        )

        # 4️⃣ Meses ya pagados
        pagados = {
            (detalle.anio_pago, detalle.mes_id): detalle.pago_id
            for detalle in PagoDetalle.objects.filter(
                pago__id_alumno_id=alumno.id_alumno,
                mes__isnull=False
            )
        }

        # 5️⃣ Inscripción
        detalle_inscripcion = PagoDetalle.objects.filter(
            pago__id_alumno_id=alumno.id_alumno,
            id_concepto_id=2
        ).first()

        inscripcion_pagada = detalle_inscripcion is not None
        pago_inscripcion = detalle_inscripcion.pago_id if detalle_inscripcion else None

        # 6️⃣ Armar respuesta
        meses_por_anio = {}

        for anio in range(anio_ingreso, anio_final + 1):

            disponibles = []

            if anio == anio_ingreso:
                disponibles.append({
                    "id_mes": 1,
                    "descripcion": "Inscripción",
                    "pagado": inscripcion_pagada,
                    "id_pago": pago_inscripcion
                })

            for mes in meses_catalogo:

                pago_id = pagados.get((anio, mes["id_mes"]))

                disponibles.append({
                    "id_mes": mes["id_mes"],
                    "descripcion": mes["descripcion"],
                    "pagado": pago_id is not None,
                    "id_pago": pago_id
                })

            meses_por_anio[str(anio)] = disponibles

        return Response({
            "alumno": alumno.id_alumno,
            "anio_ingreso": anio_ingreso,
            "anio_final": anio_final,
            "ultimo_pagado": ultimo_pagado,  # 🔥 IMPORTANTE
            "meses": meses_por_anio
        })