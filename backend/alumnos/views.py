from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Alumno
from .serializers import AlumnoSerializer

class AlumnoListCreate(APIView):
    """
    GET: Lista de alumnos con filtros por estado, carrera y búsqueda.
    POST: Crea un nuevo alumno.
    """
    def get(self, request):
        try:
            estado = request.query_params.get('estado')
            carrera = request.query_params.get('carrera')
            search = request.query_params.get('search') # <--- Campo usado por el autocomplete

            alumnos = Alumno.objects.all()

            # --- 1. FILTRO POR ESTADO ---
            # Si NO se especifica un estado Y NO estamos buscando, aplicamos el filtro por defecto (Activos ID 1).
            if not estado and not search:
                alumnos = alumnos.filter(carreras_cursadas__id_estado_id=1) 
            
            # Si el usuario pide un estado específico, lo aplicamos.
            elif estado and estado != "all":
                 alumnos = alumnos.filter(carreras_cursadas__id_estado_id=estado)
            # Si estado es 'all' o hay 'search', no se aplica ningún filtro de estado por defecto.

            # --- 2. FILTRO POR CARRERA ---
            if carrera and carrera != "all":
                alumnos = alumnos.filter(carreras_cursadas__carrera_id=carrera)

            # --- 3. BÚSQUEDA POR TEXTO ---
            if search:
                alumnos = alumnos.filter(
                    Q(nombre__icontains=search) | 
                    Q(apellido__icontains=search) | 
                    Q(dni__icontains=search)
                )

            # distinct() es vital cuando filtras por relaciones para evitar duplicados
            alumnos = alumnos.order_by('id_alumno').distinct()
            
            serializer = AlumnoSerializer(alumnos, many=True)
            return Response(serializer.data)

        except Exception as e:
            # Imprime el error real en la terminal para facilitar la depuración
            print(f"\n❌ ERROR EN GET ALUMNOS: {str(e)}\n")
            return Response(
                {"error": "Ocurrió un error en el servidor al buscar alumnos.", "detalle": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        serializer = AlumnoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlumnoDetail(APIView):
    """
    GET: Devuelve los datos de un alumno específico.
    PUT: Modifica los datos de un alumno.
    PATCH: Cambia el estado (baja o reactivación).
    DELETE: Elimina un alumno.
    """
    def get(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)
        serializer = AlumnoSerializer(alumno)
        return Response(serializer.data)

    def put(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)
        serializer = AlumnoSerializer(alumno, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)
        nuevo_estado = request.data.get('id_estado')

        if not nuevo_estado:
            return Response({"error": "Debe indicar un id_estado"}, status=status.HTTP_400_BAD_REQUEST)

        # OJO AQUÍ: Asegúrate que 'carreras_cursadas' sea el related_name correcto en models.py
        carrera = alumno.carreras_cursadas.first() 
        
        if not carrera:
            return Response({"error": "El alumno no tiene carrera cursada asociada"}, status=status.HTTP_400_BAD_REQUEST)

        carrera.id_estado_id = nuevo_estado
        carrera.save()
        return Response({"status": "estado actualizado", "nuevo_estado": nuevo_estado}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)
        alumno.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)