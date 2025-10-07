# backend/ctacte/views.py
# from django.shortcuts import render, get_object_or_404
# from alumnos.models import Alumno
# from .models import Pago
# from django.db.models import Sum
# from django.db.models.functions import Coalesce

# def pagos_por_alumno(request, alumno_id):
#     alumno = get_object_or_404(Alumno, pk=alumno_id)
#     pagos = Pago.objects.filter(alumno=alumno).order_by('-fecha_pago')
#     total = pagos.aggregate(total=Coalesce(Sum('importe_total'), 0))['total']
#     return render(request, 'ctacte/pagos_por_alumno.html', {
#         'alumno': alumno,
#         'pagos': pagos,
#         'total': total,
#     })

#================================================================================


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
        objs = Pago.objects.all().order_by('-fecha_pago', '-id_pago')
        ser = PagoSerializer(objs, many=True)
        return Response(ser.data)

    def post(self, request):
        # Si quisieras tomar el usuario del request en lugar de id_usuario en el body:
        # data = request.data.copy()
        # if request.user and request.user.is_authenticated:
        #     data['id_usuario'] = request.user.id
        # else:
        #     data = request.data
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

