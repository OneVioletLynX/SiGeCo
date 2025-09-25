from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Carrera, Estado, CarreraCursada
from .serializers import CarreraSerializer, EstadoSerializer, CarrerasCursadasSerializer

# Create your views here.

class CarreraListCreate(APIView):
    def get(self, request):
        carreras = Carrera.objects.all().order_by('id_carrera')

        serializer = CarreraSerializer(carreras, many=True)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = CarreraSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CarreraDetail(APIView):
    def get(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera)

        return Response(serializer.data)
    
    def put(self, request, pk):
        serializer = CarreraSerializer(Carrera, data=request.data)

        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        carrera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
#/////////////////////////////////////////////////////////////////////////////////////////////////////

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
    
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class EstadoDetail(APIView):
    def get(self, request, pk):
        estado = get_object_or_404(Estado, pk=pk)
        serializer = EstadoSerializer(estado)

        return Response(serializer.data)
    
    def put(self, request, pk):
        serializer = EstadoSerializer(Estado, data=request.data)

        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        estado = get_object_or_404(Estado, pk=pk)
        estado.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
#/////////////////////////////////////////////////////////////////////////////////////////////////////

class CarreraCursadasListCreate(APIView):
    def get(self, request):
        carrerasCursadas = CarreraCursada.objects.all().order_by('id_alumno')

        serializer = CarrerasCursadasSerializer(carrerasCursadas, many=True)

        return Response(serializer.data)
    
    def post(self, request):
        serializer = CarrerasCursadasSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class CarreraCursadasDetail(APIView):
    def get(self, request, pk):
        carrerasCursadas = get_object_or_404(CarreraCursada, pk=pk)
        serializer = CarrerasCursadasSerializer(carrerasCursadas)

        return Response(serializer.data)
    
    def put(self, request, pk):
        serializer = CarrerasCursadasSerializer(CarreraCursada, data=request.data)

        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        carrerasCursadas = get_object_or_404(CarreraCursada, pk=pk)
        carrerasCursadas.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)