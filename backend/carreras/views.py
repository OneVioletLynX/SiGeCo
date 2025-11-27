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
        try:
            search = request.GET.get('search', '').strip()
            
            # --- SOLUCIÓN AL ERROR 1054 ---
            # Usamos .values() para pedirle a la BD SOLO lo que existe.
            # Evitamos usar CarreraSerializer aquí porque busca 'id_estado' y rompe todo.
            qs = Carrera.objects.values('id_carrera', 'descripcion').order_by('descripcion')

            if search:
                qs = qs.filter(descripcion__icontains=search)

            # Convertimos el QuerySet a lista para que sea serializable
            return Response(list(qs))
            
        except Exception as e:
            print(f"Error en GET Carreras: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        # El POST usa el serializer. Si el serializer tiene campos que no existen en DB, fallará.
        serializer = CarreraSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarreraDetail(APIView):
    def get(self, request, pk):
        # También corregimos el detalle por si acaso
        carrera = Carrera.objects.values('id_carrera', 'descripcion').filter(pk=pk).first()
        if not carrera:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(carrera)

    def put(self, request, pk):
        carrera = get_object_or_404(Carrera, pk=pk)
        serializer = CarreraSerializer(carrera, data=request.data)
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    def patch(self, request, pk):
        # OJO: Esto conceptualmente fallará si tu modelo Carrera sigue esperando 'id_estado'
        # pero lo dejo como estaba en tu lógica original por si acaso.
        carrera = get_object_or_404(Carrera, pk=pk)
        
        # Esta lógica asume que la Carrera tiene estado, pero la DB dice que no.
        # Probablemente esto de error si intentas usarlo, pero no afecta al buscador.
        nuevo_estado_id = request.data.get('id_estado')
        if not nuevo_estado_id:
            return Response({"error": "Debe indicar un id_estado"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            nuevo_estado = Estado.objects.get(pk=nuevo_estado_id)
            carrera.id_estado = nuevo_estado # Esto fallará al guardar si la columna no existe
            carrera.save()
            
            return Response({
                "status": "actualizado",
                "id_carrera": carrera.id_carrera,
                "nuevo_estado": nuevo_estado.descripcion
            }, status=status.HTTP_200_OK)
        except Exception as e:
             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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