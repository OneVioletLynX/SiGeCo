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

        # 🔹 Filtro por estado
        if estado and estado != "all":
            alumnos = alumnos.filter(carreras_cursadas__id_estado_id=estado)

            # --- 2. FILTRO POR CARRERA ---
            if carrera and carrera != "all":
                alumnos = alumnos.filter(carreras_cursadas__carrera_id=carrera)

        # 🔹 Búsqueda general
        if search:
            alumnos = alumnos.filter(
                Q(nombre__icontains=search)
                | Q(apellido__icontains=search)
                | Q(dni__icontains=search)
            )

        # 🔹 Filtros directos para validación de unicidad
        dni = request.query_params.get('dni')
        email = request.query_params.get('email')
        legajo = request.query_params.get('legajo')

        if dni:
            alumnos = alumnos.filter(dni=dni)

        if email:
            alumnos = alumnos.filter(email=email)

        if legajo:
            alumnos = alumnos.filter(legajo=legajo)

        alumnos = alumnos.order_by('id_alumno').distinct()
        serializer = AlumnoSerializer(alumnos, many=True)
        return Response(serializer.data)


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