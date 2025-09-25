from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework import status 
from django.shortcuts import get_object_or_404 
from .models import Valor, Concepto
from .serializers import ValoresSerializer, ConceptoSerializer

class ValoresListCreate(APIView): 
    def get(self, request): 
        valores = Valor.objects.all().order_by('id') 
        serializer = ValoresSerializer(valores, many=True) 
        return Response(serializer.data) 
    def post(self, request): 
        serializer = ValoresSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValoresDetail(APIView):
    def get(self, request, pk): 
        valores = get_object_or_404(Valor, pk=pk) 
        serializer = ValoresSerializer(valores) 
        return Response(serializer.data) 
    def put(self, request, pk): 
        valores = get_object_or_404(Valor, pk=pk) 
        serializer = ValoresSerializer(valores, data=request.data) 
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    def delete(self, request, pk): 
        valores = get_object_or_404(Valor, pk=pk) 
        valores.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConceptoListCreate(APIView): 
    def get(self, request): 
        conceptos = Concepto.objects.all().order_by('id') 
        serializer = ConceptoSerializer(conceptos, many=True) 
        return Response(serializer.data) 
    def post(self, request): 
        serializer = ConceptoSerializer(data=request.data) 
        if serializer.is_valid(): 
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConceptoDetail(APIView):
    def get(self, request, pk): 
        conceptos = get_object_or_404(Concepto, pk=pk) 
        serializer = ConceptoSerializer(conceptos) 
        return Response(serializer.data) 
    def put(self, request, pk): 
        conceptos = get_object_or_404(Concepto, pk=pk) 
        serializer = ConceptoSerializer(conceptos, data=request.data) 
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    def delete(self, request, pk): 
        conceptos = get_object_or_404(Concepto, pk=pk) 
        conceptos.delete() 
        return Response(status=status.HTTP_204_NO_CONTENT)