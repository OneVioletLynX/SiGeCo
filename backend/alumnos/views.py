from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from .models import Alumno
from .serializers import AlumnoSerializer
from carreras.models import CarreraCursada
from auditoria.models import registrar


def _alumno_qs():
    return Alumno.objects.prefetch_related(
        Prefetch(
            'carreras_cursadas',
            queryset=CarreraCursada.objects.select_related('carrera', 'id_estado')
        )
    )


class AlumnoListCreate(APIView):
    def get(self, request):
        estado  = request.query_params.get('estado')
        carrera = request.query_params.get('carrera')
        search  = request.query_params.get('search')

        alumnos = _alumno_qs()

        # Por defecto solo activos; pasar estado=all para ver todos
        if estado == "all":
            pass
        elif estado:
            alumnos = alumnos.filter(carreras_cursadas__id_estado_id=estado)
        else:
            alumnos = alumnos.filter(carreras_cursadas__id_estado_id=1)

        if carrera and carrera != "all":
            alumnos = alumnos.filter(carreras_cursadas__carrera_id=carrera)

        if search:
            alumnos = alumnos.filter(
                Q(nombre__icontains=search)
                | Q(apellido__icontains=search)
                | Q(dni__icontains=search)
            )

        dni    = request.query_params.get('dni')
        email  = request.query_params.get('email')
        legajo = request.query_params.get('legajo')

        if dni:    alumnos = alumnos.filter(dni=dni)
        if email:  alumnos = alumnos.filter(email=email)
        if legajo: alumnos = alumnos.filter(legajo=legajo)

        alumnos = alumnos.order_by('apellido', 'nombre').distinct()
        return Response(AlumnoSerializer(alumnos, many=True).data)

    def post(self, request):
        serializer = AlumnoSerializer(data=request.data)
        if serializer.is_valid():
            alumno = serializer.save()
            registrar(request, 'ALTA', 'alumno',
                      f"Alta de alumno: {alumno.apellido}, {alumno.nombre}",
                      alumno.id_alumno)
            return Response(serializer.data, status=201)
        print(serializer.errors)
        return Response(serializer.errors, status=400)


class AlumnoDetail(APIView):
    def get(self, request, pk):
        alumno = get_object_or_404(_alumno_qs(), pk=pk)
        return Response(AlumnoSerializer(alumno).data)

    def put(self, request, pk):
        alumno     = get_object_or_404(Alumno, pk=pk)
        serializer = AlumnoSerializer(alumno, data=request.data)
        if serializer.is_valid():
            serializer.save()
            registrar(request, 'MODIFICACION', 'alumno',
                      f"Modificación de alumno: {alumno.apellido}, {alumno.nombre}", pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)

        if list(request.data.keys()) == ['id_estado']:
            nuevo_estado = request.data.get('id_estado')
            carrera = alumno.carreras_cursadas.first()
            if not carrera:
                return Response({"error": "El alumno no tiene carrera asociada"}, status=400)
            carrera.id_estado_id = nuevo_estado
            carrera.save()
            accion = 'BAJA' if nuevo_estado == 2 else 'MODIFICACION'
            label  = 'Baja'  if nuevo_estado == 2 else 'Reactivación'
            registrar(request, accion, 'alumno',
                      f"{label} de alumno: {alumno.apellido}, {alumno.nombre}", pk)
            return Response({"status": "estado actualizado"})

        serializer = AlumnoSerializer(alumno, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            registrar(request, 'MODIFICACION', 'alumno',
                      f"Modificación de alumno: {alumno.apellido}, {alumno.nombre}", pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        alumno = get_object_or_404(Alumno, pk=pk)
        nombre = f"{alumno.apellido}, {alumno.nombre}"
        alumno.delete()
        registrar(request, 'BAJA', 'alumno', f"Eliminación de alumno: {nombre}", pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
