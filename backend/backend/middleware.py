from django.http import JsonResponse
from .permisos import tiene_permiso, seccion_desde_path

# Rutas de la API que son públicas (no requieren autenticación ni rol)
RUTAS_API_PUBLICAS = [
    '/usuarios/api/login/',
    '/api/token/',
]


class RolMiddleware:
    """
    Middleware del backend que valida que el usuario autenticado
    tenga permiso de acceder a la sección solicitada.

    Se ejecuta después de la autenticación JWT — request.user
    ya es un objeto Usuario con su rol cargado.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Saltear rutas públicas y no-API
        if path in RUTAS_API_PUBLICAS:
            return self.get_response(request)

        if not (path.startswith('/api/') or path.startswith('/ctacte/')):
            return self.get_response(request)

        # Si el usuario no está autenticado, DRF ya devuelve 401 antes
        if not hasattr(request, 'user') or not request.user or not getattr(request.user, 'is_authenticated', False):
            return self.get_response(request)

        # Verificar permiso por sección
        seccion = seccion_desde_path(path)
        if seccion and not tiene_permiso(request.user.rol, seccion):
            return JsonResponse(
                {"error": f"No tenés permiso para acceder a '{seccion}'."},
                status=403
            )

        return self.get_response(request)