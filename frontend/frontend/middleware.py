from django.shortcuts import redirect

# Rutas que no requieren autenticación
RUTAS_PUBLICAS = ['/', '/login/']


class TokenCookieMiddleware:
    """
    Middleware del frontend que verifica la cookie sigeco_access
    antes de servir cualquier página protegida.

    Si no hay cookie → redirige al login.
    Esto protege las rutas incluso con JavaScript deshabilitado.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Rutas públicas: login y raíz
        if request.path in RUTAS_PUBLICAS:
            return self.get_response(request)

        # Archivos estáticos: nunca bloquear
        if request.path.startswith('/static/'):
            return self.get_response(request)

        # Verificar cookie
        token = request.COOKIES.get('sigeco_access')
        if not token:
            return redirect('/')

        return self.get_response(request)


class AdminRouteMiddleware:
    """
    Bloquea server-side el acceso a /administracion/ si la cookie no está.
    La verificación del rol ADMIN se hace en JS (base.html).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/administracion/'):
            token = request.COOKIES.get('sigeco_access')
            if not token:
                return redirect('/')
        return self.get_response(request)