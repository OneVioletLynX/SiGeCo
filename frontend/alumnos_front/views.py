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

    alumno = get_object_or_404(Alumno, id_alumno=alumno_id)

    carreras = CarreraCursada.objects.select_related(
        "carrera", "id_estado"
    ).filter(alumno=alumno)

    # La tabla geografia_localidad usa IDs INDEC — algunos alumnos pueden
    # tener ciudad_id que no existe en esa tabla.
    try:
        localidad = alumno.ciudad
        ciudad_nombre = localidad.nombre if localidad else "—"
        try:
            provincia_nombre = localidad.departamento.provincia.nombre
        except Exception:
            provincia_nombre = "—"
    except Exception:
        ciudad_nombre = "—"
        provincia_nombre = "—"

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
            "alumno":           alumno,
            "carreras":         carreras,
            "ciudad_nombre":    ciudad_nombre,
            "provincia_nombre": provincia_nombre,
            "edad":             edad,
        }
    )