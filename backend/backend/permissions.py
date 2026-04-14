from rest_framework.permissions import BasePermission
from .permisos import tiene_permiso, seccion_desde_path


class TienePermisoRol(BasePermission):
    """
    Verifica que el rol del usuario tenga acceso a la sección
    correspondiente al endpoint solicitado.
    """
    message = "No tenés permiso para acceder a esta sección."

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False

        seccion = seccion_desde_path(request.path)

        # Si el path no mapea a ninguna sección, permitir
        if not seccion:
            return True

        return tiene_permiso(request.user.rol, seccion)