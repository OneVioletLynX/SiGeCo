from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Carrera, Estado, CarreraCursada
from .serializers import CarreraSerializer, EstadoSerializer, CarrerasCursadasSerializer

# ============================================================================
# 1. VISTAS DE CARRERA (CORREGIDAS PARA EVITAR ERROR DE COLUMNA FANTASMA)
# ============================================================================

class CarreraListCreate(APIView):

    def get(self, request):
        carreras = Carrera.objects.all().order_by("descripcion")
        serializer = CarreraSerializer(carreras, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CarreraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CarreraDetail(APIView):
    def get(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera)
        return Response(serializer.data)
    

    def put(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera, data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def patch(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        carrera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    
# ============================================================================
# 2. VISTAS DE ESTADO (SIN CAMBIOS)
# ============================================================================

class EstadoListCreate(APIView):
    def get(self, request):
        estados = Estado.objects.all().order_by('id_estado')
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
        estado = get_object_or_404(Estado, pk=pk)
        serializer = EstadoSerializer(estado)
        return Response(serializer.data)
    
    def put(self, request, pk):
        # Corrección menor: 'Estado' es la clase, debes buscar la instancia primero
        estado = get_object_or_404(Estado, pk=pk)
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
# 3. VISTAS DE CURSADAS (SIN CAMBIOS)
# ============================================================================

class CarreraCursadasListCreate(APIView):
    def get(self, request):
        carrerasCursadas = CarreraCursada.objects.all().order_by('alumno_id')
        serializer = CarrerasCursadasSerializer(carrerasCursadas, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CarrerasCursadasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CarreraCursadasDetail(APIView):
    def get_object(self, alumno_id, carrera_id):
        return get_object_or_404(
            CarreraCursada,
            alumno_id=alumno_id,
            carrera_id=carrera_id
        )

    def get(self, request, alumno_id, carrera_id):
        carrerasCursadas = self.get_object(alumno_id, carrera_id)
        serializer = CarrerasCursadasSerializer(carrerasCursadas)
        return Response(serializer.data)

    def put(self, request, alumno_id, carrera_id):
        carrerasCursadas = self.get_object(alumno_id, carrera_id)
        serializer = CarrerasCursadasSerializer(
            carrerasCursadas, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, alumno_id, carrera_id):
        carrerasCursadas = self.get_object(alumno_id, carrera_id)
        carrerasCursadas.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)