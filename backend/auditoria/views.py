from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import RegistroAuditoria


@require_GET
def lista_auditoria(request):
    limit = min(int(request.GET.get('limit', 20)), 100)
    qs = RegistroAuditoria.objects.all()[:limit]
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
