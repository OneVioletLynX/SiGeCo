from django.shortcuts import render

def reportes_index(request):
    return render(request, 'reportes/reportes_index.html')

def reportes_alumnos(request):
    return render(request, 'reportes/reportes_alumnos.html')

def reportes_bonos(request):
    return render(request, 'reportes/reportes_bonos.html')

def dashboard_estadisticas(request):
    return render(request, 'reportes/dashboard_estadisticas.html')