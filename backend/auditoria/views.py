from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import RegistroAuditoria


@require_GET
def lista_auditoria(request):
    limit      = min(int(request.GET.get('limit', 20)), 200)
    entidad    = request.GET.get('entidad')
    entidad_id = request.GET.get('entidad_id')

    qs = RegistroAuditoria.objects.all()
    if entidad:
        qs = qs.filter(entidad=entidad)
    if entidad_id:
        qs = qs.filter(entidad_id=entidad_id)
    qs = qs[:limit]
    data = [
        {
            "id":             r.id,
            "accion":         r.accion,
            "entidad":        r.entidad,
            "entidad_id":     r.entidad_id,
            "descripcion":    r.descripcion,
            "usuario_nombre": r.usuario_nombre or "Sistema",
            "fecha":          r.fecha.isoformat(),
        }
        for r in qs
    ]
    return JsonResponse(data, safe=False)
