from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from usuarios.models import Usuario


class UsuarioJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que busca el usuario en usuarios_usuario
    en lugar de la tabla auth_user de Django.
    """

    def get_user(self, validated_token):
        try:
            usuario_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token no contiene un ID de usuario válido.")

        try:
            return Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            raise InvalidToken("Usuario no encontrado.")