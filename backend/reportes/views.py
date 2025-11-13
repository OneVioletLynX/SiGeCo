from django.http.response import JsonResponse
from reportes.services import get_contabilidad_data, get_alumnos_data, get_admin_data



def seccion_contabilidad(request):
    return JsonResponse(get_contabilidad_data())

def seccion_alumnos(request):
    return JsonResponse(get_alumnos_data())

def seccion_admin(request):
    return JsonResponse(get_admin_data())