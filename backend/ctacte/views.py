from datetime import date
<<<<<<< HEAD
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
=======
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from rest_framework.views import APIView
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

# Modelos
from alumnos.models import Alumno
<<<<<<< HEAD
from django.utils import timezone
=======
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
from .models import MesPago, MetodoPago, Pago, PagoDetalle

# Serializers
from .serializers import (
    MesPagoSerializer, MetodoPagoSerializer, PagoSerializer, PagoDetalleSerializer
)

<<<<<<< HEAD
@api_view(['GET'])
def ctacte_api_root(request):
    return Response({
        'meses': request.build_absolute_uri('meses/'),
        'metodos-pagos': request.build_absolute_uri('metodos-pagos/'),
        'pagos': request.build_absolute_uri('pagos/'),
        'pagos-detalle': request.build_absolute_uri('pagos-detalle/'),
    })

=======
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


>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
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
<<<<<<< HEAD
        alumno_id = request.query_params.get('alumno')
        pagos = Pago.objects.all().order_by('-fecha_pago', '-id_pago')
        if alumno_id:
            pagos = pagos.filter(id_alumno_id=alumno_id)

        ser = PagoSerializer(pagos, many=True)
        return Response(ser.data)

    def post(self, request):
        ser = PagoSerializer(data=request.data)
=======
        """
        Lista de pagos con:
         - búsqueda por ?q= (id_alumno.nombre, apellido o id_pago)
         - paginación ?page= & ?page_size=
         - orden por fecha desc
        """
        q = request.GET.get('q', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        qs = Pago.objects.select_related('id_alumno').all().order_by('-fecha_pago', '-id_pago')

        if q:
            filters = Q(id_alumno__nombre__icontains=q) | Q(id_alumno__apellido__icontains=q)
            if q.isdigit():
                filters |= Q(id_pago=int(q))
            qs = qs.filter(filters)

        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        ser = PagoSerializer(page_obj.object_list, many=True, context={'request': request})
        
        # Paginación manual para respuesta JSON
        base_url = request.build_absolute_uri(request.path)
        def page_url(p):
            params = request.GET.copy()
            params['page'] = p
            return f"{base_url}?{params.urlencode()}"

        result = {
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'num_pages': paginator.num_pages,
            'next': page_url(page + 1) if page < paginator.num_pages else None,
            'previous': page_url(page - 1) if page > 1 else None,
            'results': ser.data,
        }
        return Response(result)

    def post(self, request):
        ser = PagoSerializer(data=request.data, context={'request': request})
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
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
<<<<<<< HEAD
        objs = PagoDetalle.objects.all().order_by('id_detalle')
        ser = PagoDetalleSerializer(objs, many=True)
        return Response(ser.data)
=======
        qs = PagoDetalle.objects.select_related('pago', 'mes').all().order_by('pago_id', 'mes_id')

        # Filtros
        pago = request.GET.get('pago')
        if pago:
            qs = qs.filter(pago_id=pago)

        mes = request.GET.get('mes')
        if mes:
            qs = qs.filter(mes_id=mes)

        # Paginación
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 100))
        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        ser = PagoDetalleSerializer(page_obj.object_list, many=True)
        result = {
            'count': paginator.count,
            'page': page,
            'page_size': page_size,
            'num_pages': paginator.num_pages,
            'results': ser.data,
        }
        return Response(result)
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f

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
<<<<<<< HEAD
=======


# -------- Lógica de Negocio Compleja --------

>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
class RegistrarPago(APIView):
    def post(self, request):
        try:
            data = request.data
            alumno_id = data.get("id_alumno")
            metodo_id = data.get("id_metodo_pago")
            meses_ids = data.get("meses", [])
            importe_total = float(data.get("importe_total"))
            anio_req = data.get("anio")  # opcional

            if not alumno_id or not metodo_id or not meses_ids:
                return Response({"error": "Faltan datos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

            alumno = Alumno.objects.get(pk=alumno_id)
            metodo = MetodoPago.objects.get(pk=metodo_id)
            
            # Usar año actual si no viene en el request
            anio_pago = int(anio_req) if anio_req else timezone.now().year

            # 1. Crear la cabecera del Pago
            pago = Pago.objects.create(
                id_alumno=alumno,
                id_metodo_pago=metodo,
                fecha_pago=timezone.now(),
                importe_total=importe_total
            )

            # 2. Calcular y crear los detalles
            importe_por_mes = round(importe_total / len(meses_ids), 2)
            
            for mes_id in meses_ids:
                mes = MesPago.objects.get(pk=mes_id)
                PagoDetalle.objects.create(
                    pago=pago,
                    mes=mes,
                    anio_pago=anio_pago,
                    id_concepto_id=1,  # IMPORTANTE: Asegurate que el ID 1 (Cuota) exista en tabla Conceptos
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
    Calcula qué meses debe el alumno basándose en su año de ingreso
    y su último pago realizado.
    """

    def get(self, request):
        alumno_id = request.query_params.get("alumno")
        if not alumno_id:
            return Response({"error": "Falta el parámetro alumno"}, status=status.HTTP_400_BAD_REQUEST)

        alumno = get_object_or_404(Alumno, pk=alumno_id)

        # 1) AÑO DE INGRESO
        # Si anio_ingreso es None, usar el año de inscripción
        anio_ingreso = alumno.anio_ingreso or alumno.inscripcion.year

        # 2) ÚLTIMO AÑO PAGADO
        ult_pago = (
            PagoDetalle.objects
            .filter(pago__id_alumno_id=alumno.id_alumno)
            .exclude(anio_pago__isnull=True)
            .order_by("-anio_pago")
            .values_list("anio_pago", flat=True)
            .first()
        )

        if ult_pago:
            # Si pagó 2024, mostramos hasta 2025 (anio_final + 1)
            # El max asegura que no vayamos hacia atrás si el ingreso es posterior
            anio_final = max(anio_ingreso, ult_pago + 1)
        else:
<<<<<<< HEAD
            anio_final = anio_ingreso + 1  # Nunca pagó nada

        # -------------------------
        # 3) MESES CATALOGO (Sin inscripción)
        # -------------------------
=======
            # Si nunca pagó nada, mostramos ingreso y el siguiente
            anio_final = anio_ingreso + 1

        # 3) MESES CATALOGO (Enero, Febrero...)
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
        meses_catalogo = list(
            MesPago.objects
            .exclude(descripcion__icontains="insc")  # ⛔ evitar inscripción aquí
            .order_by("id_mes")
            .values("id_mes", "descripcion")
        )

        # 4) MESES YA PAGADOS (Tupla: año, mes_id)
        pagados = set(
            PagoDetalle.objects
            .filter(pago__id_alumno_id=alumno.id_alumno, mes__isnull=False)
            .values_list("anio_pago", "mes_id")
        )

<<<<<<< HEAD
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
=======
        # 5) ARMAR RESPUESTA POR AÑO
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
        meses_por_anio = {}

        for anio in range(anio_ingreso, anio_final + 1):
            disponibles = []
<<<<<<< HEAD

            # Agregar inscripción SOLO en el año de ingreso
            if anio == anio_ingreso and inscripcion_pendiente:
                disponibles.append({
                    "id_mes": 1,  # ID real de Inscripción
                    "descripcion": "Inscripción"
                })

            # Agregar meses comunes (enero–diciembre)
=======
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
            for mes in meses_catalogo:
                # Si la combinación (2025, Marzo) no está pagada, se agrega
                if (anio, mes["id_mes"]) not in pagados:
                    disponibles.append({
                        "id_mes": mes["id_mes"],
                        "descripcion": mes["descripcion"]
                    })
            if disponibles:
                meses_por_anio[str(anio)] = disponibles

<<<<<<< HEAD
            meses_por_anio[str(anio)] = disponibles

        # -------------------------
        # 7) RESPUESTA
        # -------------------------
=======
        # 6) INSCRIPCIÓN PENDIENTE (Verificar Concepto ID 2)
        # IMPORTANTE: Asegurate que el ID 2 sea 'Inscripción' en tu BD
        inscripcion_pendiente = not PagoDetalle.objects.filter(
            pago__id_alumno_id=alumno.id_alumno,
            id_concepto_id=2 
        ).exists()

>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
        return Response({
            "alumno": alumno.id_alumno,
            "anio_ingreso": anio_ingreso,
            "anio_final": anio_final,
            "inscripcion_pendiente": inscripcion_pendiente,
            "meses": meses_por_anio
<<<<<<< HEAD
        })
=======
        })
>>>>>>> 62599f47832da27fc8dd1e1c65c40bf41d49295f
