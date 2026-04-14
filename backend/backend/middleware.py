from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

class JWTMiddleware:
    RUTAS_PUBLICAS = ['/', '/usuarios/api/login/', '/api/token/']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not any(request.path.startswith(r) for r in self.RUTAS_PUBLICAS):
            auth = request.headers.get('Authorization', '')
            if not auth.startswith('Bearer '):
                from django.http import JsonResponse
                return JsonResponse({'error': 'No autenticado'}, status=401)
        return self.get_response(request)