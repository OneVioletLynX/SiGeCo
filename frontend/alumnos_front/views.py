from django.shortcuts import render

# Create your views here.

def alumnos(request):
    return render(request, 'alumnos/index.html')

def alumno_nuevo(request):
    return render(request, "alumnos/alumno_form.html")