from datetime import date
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Valor, Concepto
from .serializers import ValorSerializer, ConceptoSerializer


# --- CRUD de Valores ---
class ValoresListCreate(APIView):
    def get(self, request):
        valores = Valor.objects.all().order_by("id_valor")
        serializer = ValorSerializer(valores, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ValorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ValoresDetail(APIView):
    def get(self, request, pk):
        valor = get_object_or_404(Valor, pk=pk)
        serializer = ValorSerializer(valor)
        return Response(serializer.data)

    def put(self, request, pk):
        valor = get_object_or_404(Valor, pk=pk)
        serializer = ValorSerializer(valor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        valor = get_object_or_404(Valor, pk=pk)
        valor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- NUEVO ENDPOINT: Valor vigente ---
class ValorVigenteView(APIView):
    """
    Devuelve el valor vigente para una carrera, un concepto y una fecha.
    Si la fecha es mayor al último valor, devuelve el último.
    Si la fecha es anterior al primero, devuelve el primero.
    """
    def get(self, request):
        carrera = request.query_params.get("carrera")
        concepto = request.query_params.get("concepto")
        fecha_str = request.query_params.get("fecha")
        
        if not carrera or not concepto:
            return Response({"error": "Debe indicar carrera y concepto"}, status=400)

        try:
            fecha = date.fromisoformat(fecha_str) if fecha_str else date.today()
        except:
            return Response({"error": "Fecha inválida"}, status=400)

        # 1) Primer intento: valor vigente exacto
        valor = (
            Valor.objects
            .filter(id_carrera=carrera, id_concepto=concepto, fecha_inicio__lte=fecha)
            .order_by("-fecha_inicio")
            .first()
        )

        if valor:
            # Se encontró uno válido → devolverlo
            return Response(ValorSerializer(valor).data)

        # 2) Si NO se encontró (la fecha es anterior a todos)
        # devolver el PRIMERO cargado (el más antiguo)
        valor = (
            Valor.objects
            .filter(id_carrera=carrera, id_concepto=concepto)
            .order_by("fecha_inicio")
            .first()
        )

        if not valor:
            return Response({"error": "No hay valores disponibles"}, status=404)

        return Response(ValorSerializer(valor).data)


# --- CRUD de Conceptos ---
class ConceptoListCreate(APIView):
    def get(self, request):
        conceptos = Concepto.objects.all().order_by("id_concepto")
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
        concepto = get_object_or_404(Concepto, pk=pk)
        serializer = ConceptoSerializer(concepto)
        return Response(serializer.data)

    def put(self, request, pk):
        concepto = get_object_or_404(Concepto, pk=pk)
        serializer = ConceptoSerializer(concepto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        concepto = get_object_or_404(Concepto, pk=pk)
        concepto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
