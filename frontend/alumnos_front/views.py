from django.shortcuts import render, get_object_or_404
from backend.alumnos.models import Alumno
from backend.carreras.models import CarreraCursada
from backend.geografia.models import Localidad
from datetime import date
# Create your views here.

def alumnos(request):
    return render(request, 'alumnos/index.html')

def alumno_nuevo(request):
    return render(request, "alumnos/alumno_form.html")

def ficha_alumno(request, alumno_id):

    alumno = Alumno.objects.select_related(
        "ciudad__departamento__provincia"
    ).get(id_alumno=alumno_id)

    carreras = CarreraCursada.objects.select_related(
        "carrera",
        "id_estado"
    ).filter(alumno=alumno)

    localidad = alumno.ciudad

    # calcular edad
    edad = None
    if alumno.fecha_nacimiento:
        hoy = date.today()
        edad = hoy.year - alumno.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (alumno.fecha_nacimiento.month, alumno.fecha_nacimiento.day)
        )

    return render(
        request,
        "alumnos/alumno_ficha.html",
        {
            "alumno": alumno,
            "carreras": carreras,
            "localidad": localidad,
            "edad": edad
        }
    )