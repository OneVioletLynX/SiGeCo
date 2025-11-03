from django.shortcuts import render

# Create your views here.

def alumnos(request):
    return render(request, 'alumnos/index.html')