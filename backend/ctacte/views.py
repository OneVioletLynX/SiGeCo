# app_name/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from alumnos.models import Alumno
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from .models import MesPago, MetodoPago, Pago, PagoDetalle
from .serializers import (
    MesPagoSerializer, MetodoPagoSerializer, PagoSerializer, PagoDetalleSerializer
)

@api_view(['GET'])
def ctacte_api_root(request):
    return Response({
        'meses': request.build_absolute_uri('meses/'),
        'metodos-pagos': request.build_absolute_uri('metodos-pagos/'),
        'pagos': request.build_absolute_uri('pagos/'),
        'pagos-detalle': request.build_absolute_uri('pagos-detalle/'),
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


# -------- MetodoPago (sin cambios) --------
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
        try:
            data = request.data
            alumno_id = data.get("id_alumno")
            metodo_id = data.get("id_metodo_pago")
            meses_ids = data.get("meses", [])
            importe_total = float(data.get("importe_total"))
            anio_req = data.get("anio")  # opcional: si el front lo envía

            if not alumno_id or not metodo_id or not meses_ids:
                return Response({"error": "Faltan datos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

            alumno = Alumno.objects.get(pk=alumno_id)
            metodo = MetodoPago.objects.get(pk=metodo_id)

            anio_pago = int(anio_req) if anio_req else timezone.now().year

            pago = Pago.objects.create(
                id_alumno=alumno,
                id_metodo_pago=metodo,
                fecha_pago=timezone.now(),
                importe_total=importe_total
            )

            importe_por_mes = round(importe_total / len(meses_ids), 2)
            for mes_id in meses_ids:
                mes = MesPago.objects.get(pk=mes_id)
                PagoDetalle.objects.create(
                    pago=pago,
                    mes=mes,
                    anio_pago=anio_pago,
                    id_concepto_id=1,  # 1 = Cuota
                    importe=importe_por_mes
                )

            return Response({
                "success": True,
                "id_pago": pago.id_pago,
                "alumno": f"{alumno.apellido}, {alumno.nombre}",
                "importe_total": importe_total,
                "anio_pago": anio_pago,
                "cantidad_meses": len(meses_ids)
            }, status=status.HTTP_201_CREATED)

        except Alumno.DoesNotExist:
            return Response({"error": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except MetodoPago.DoesNotExist:
            return Response({"error": "Método de pago no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except MesPago.DoesNotExist:
            return Response({"error": "Mes no válido"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MesesPendientes(APIView):
    """
    GET /api/ctacte/pendientes/?alumno=<id>

    Devuelve:
    - anio_ingreso
    - inscripcion_pendiente (True/False)
    - meses { "2026": [...], "2027": [...], ... }
    """

    def get(self, request):
        alumno_id = request.query_params.get("alumno")
        if not alumno_id:
            return Response({"error": "Falta el parámetro alumno"}, status=status.HTTP_400_BAD_REQUEST)

        alumno = get_object_or_404(Alumno, pk=alumno_id)

        # -------------------------
        # 1) AÑO DE INGRESO
        # -------------------------
        anio_ingreso = alumno.anio_ingreso or alumno.inscripcion.year

        # -------------------------
        # 2) ÚLTIMO AÑO PAGADO
        # -------------------------
        ult_pago = (
            PagoDetalle.objects
            .filter(pago__id_alumno_id=alumno.id_alumno)
            .exclude(anio_pago__isnull=True)
            .order_by("-anio_pago")
            .values_list("anio_pago", flat=True)
            .first()
        )

        if ult_pago:
            anio_final = max(anio_ingreso, ult_pago + 1)
        else:
            anio_final = anio_ingreso + 1  # Nunca pagó nada

        # -------------------------
        # 3) MESES CATALOGO (Sin inscripción)
        # -------------------------
        meses_catalogo = list(
            MesPago.objects
            .exclude(descripcion__icontains="insc")  # ⛔ evitar inscripción aquí
            .order_by("id_mes")
            .values("id_mes", "descripcion")
        )

        # -------------------------
        # 4) MESES YA PAGADOS
        # -------------------------
        pagados = set(
            PagoDetalle.objects
            .filter(pago__id_alumno_id=alumno.id_alumno, mes__isnull=False)
            .values_list("anio_pago", "mes_id")
        )

        # -------------------------
        # 5) INSCRIPCIÓN PAGADA O NO
        # -------------------------
        inscripcion_pendiente = not PagoDetalle.objects.filter(
            pago__id_alumno_id=alumno.id_alumno,
            id_concepto_id=2   # concepto = INSCRIPCIÓN
        ).exists()

        # -------------------------
        # 6) ARMAR RESPUESTA FINAL
        # -------------------------
        meses_por_anio = {}

        for anio in range(anio_ingreso, anio_final + 1):
            disponibles = []

            # Agregar inscripción SOLO en el año de ingreso
            if anio == anio_ingreso and inscripcion_pendiente:
                disponibles.append({
                    "id_mes": 1,  # ID real de Inscripción
                    "descripcion": "Inscripción"
                })

            # Agregar meses comunes (enero–diciembre)
            for mes in meses_catalogo:
                if (anio, mes["id_mes"]) not in pagados:
                    disponibles.append({
                        "id_mes": mes["id_mes"],
                        "descripcion": mes["descripcion"]
                    })

            meses_por_anio[str(anio)] = disponibles

        # -------------------------
        # 7) RESPUESTA
        # -------------------------
        return Response({
            "alumno": alumno.id_alumno,
            "anio_ingreso": anio_ingreso,
            "anio_final": anio_final,
            "inscripcion_pendiente": inscripcion_pendiente,
            "meses": meses_por_anio
        })
