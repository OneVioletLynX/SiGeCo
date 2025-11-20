# app_name/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

from .models import MesPago, MetodoPago, Pago, PagoDetalle
from .serializers import (
    MesPagoSerializer, MetodoPagoSerializer, PagoSerializer, PagoDetalleSerializer
)


def home_ctacte(request):
    return render(request, "ctacte/home.html")


@api_view(['GET'])
def ctacte_api_root(request):
    return Response({
        'meses': request.build_absolute_uri(reverse('ctacte:meses-list')),
        'metodos-pagos': request.build_absolute_uri(reverse('ctacte:metodos-list')),
        'pagos': request.build_absolute_uri(reverse('ctacte:pagos-list')),
        'pagos-detalle': request.build_absolute_uri(reverse('ctacte:pagos-detalle-list')),
    })


# -------- MesPago (sin cambios) --------
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
        """
        Lista de pagos con:
         - búsqueda por ?q= (id_alumno.nombre o id_pago)
         - paginación ?page= & ?page_size=
         - orden por fecha desc (definido en Meta del modelo)
        """
        q = request.GET.get('q', '').strip()
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        qs = Pago.objects.select_related('id_alumno').all().order_by('-fecha_pago', '-id_pago')

        if q:
            # Si q es numérico, dejamos que busque por id_pago también
            filters = Q(id_alumno__nombre__icontains=q) | Q(id_alumno__apellido__icontains=q)  # apellido si existe
            if q.isdigit():
                filters |= Q(id_pago=int(q))
            qs = qs.filter(filters)

        paginator = Paginator(qs, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        ser = PagoSerializer(page_obj.object_list, many=True, context={'request': request})
        # respuesta estilo paginada
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
        # base queryset
        qs = PagoDetalle.objects.select_related('pago', 'mes').all().order_by('pago_id', 'mes_id')

        # filtros por query params
        pago = request.GET.get('pago')
        if pago:
            qs = qs.filter(pago_id=pago)

        mes = request.GET.get('mes')
        if mes:
            qs = qs.filter(mes_id=mes)

        # paginación
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
