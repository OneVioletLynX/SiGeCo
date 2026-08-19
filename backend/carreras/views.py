from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Carrera, Estado, CarreraCursada
from .serializers import CarreraSerializer, EstadoSerializer, CarrerasCursadasSerializer
from auditoria.models import registrar


# ============================================================================
# 1. VISTAS DE CARRERA
# ============================================================================

class CarreraListCreate(APIView):

    def get(self, request):
        carreras   = Carrera.objects.all().order_by("descripcion")
        serializer = CarreraSerializer(carreras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarreraSerializer(data=request.data)
        if serializer.is_valid():
            carrera = serializer.save()
            registrar(request, 'ALTA', 'carrera',
                      f"Alta de carrera: {carrera.descripcion}",
                      carrera.id_carrera)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarreraDetail(APIView):

    def get(self, request, pk):
        carrera    = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera)
        return Response(serializer.data)

    def put(self, request, pk):
        carrera    = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera, data=request.data)
        if serializer.is_valid():
            serializer.save()
            registrar(request, 'MODIFICACION', 'carrera',
                      f"Modificación de carrera: {carrera.descripcion}", pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        carrera    = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            nuevo_estado = request.data.get('id_estado')
            accion  = 'BAJA' if nuevo_estado == 2 else 'MODIFICACION'
            label   = 'Baja' if nuevo_estado == 2 else 'Modificación'
            registrar(request, accion, 'carrera',
                      f"{label} de carrera: {carrera.descripcion}", pk)

            if nuevo_estado == 2 and request.data.get('inactivar_alumnos'):
                estado_inactivo = Estado.objects.filter(descripcion__iexact="Inactivo").first()
                if estado_inactivo:
                    CarreraCursada.objects.filter(
                        carrera=carrera,
                        id_estado__descripcion__iexact="Activo"
                    ).update(id_estado=estado_inactivo)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        nombre  = carrera.descripcion
        carrera.delete()
        registrar(request, 'BAJA', 'carrera', f"Eliminación de carrera: {nombre}", pk)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 2. VISTAS DE ESTADO
# ============================================================================

class EstadoListCreate(APIView):
    def get(self, request):
        estados    = Estado.objects.all().order_by('id_estado')
        serializer = EstadoSerializer(estados, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EstadoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EstadoDetail(APIView):
    def get(self, request, pk):
        estado     = get_object_or_404(Estado, pk=pk)
        serializer = EstadoSerializer(estado)
        return Response(serializer.data)

    def put(self, request, pk):
        estado     = get_object_or_404(Estado, pk=pk)
        serializer = EstadoSerializer(estado, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        estado = get_object_or_404(Estado, pk=pk)
        estado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# 3. VISTAS DE CURSADAS
# ============================================================================

class CarreraCursadasListCreate(APIView):
    def get(self, request):
        qs         = CarreraCursada.objects.all().order_by('alumno_id')
        serializer = CarrerasCursadasSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarrerasCursadasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CarreraCursadasDetail(APIView):
    def get_object(self, alumno_id, carrera_id):
        return get_object_or_404(CarreraCursada, alumno_id=alumno_id, carrera_id=carrera_id)

    def get(self, request, alumno_id, carrera_id):
        obj        = self.get_object(alumno_id, carrera_id)
        serializer = CarrerasCursadasSerializer(obj)
        return Response(serializer.data)

    def put(self, request, alumno_id, carrera_id):
        obj        = self.get_object(alumno_id, carrera_id)
        serializer = CarrerasCursadasSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, alumno_id, carrera_id):
        obj = self.get_object(alumno_id, carrera_id)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
