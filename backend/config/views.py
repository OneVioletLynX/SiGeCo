from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
import re

from .models import ConfigInstituto


class EsAdmin(IsAuthenticated):
    message = "Solo los administradores pueden acceder a esta sección."

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and getattr(request.user, 'rol', None) == 'ADMIN'
        )


# =====================================================
# API — config del instituto
# =====================================================
class ConfigAPI(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [EsAdmin()]

    def get(self, request):
        config = ConfigInstituto.get()
        return Response({
            "nombre":         config.nombre,
            "color_primario": config.color_primario,
        })

    def put(self, request):
        config         = ConfigInstituto.get()
        nombre         = request.data.get("nombre", "").strip()
        color_primario = request.data.get("color_primario", "").strip()

        if not nombre:
            return Response({"error": "El nombre no puede estar vacío."}, status=400)
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color_primario):
            return Response({"error": "Color inválido. Debe ser hexadecimal, ej: #053D4E"}, status=400)

        config.nombre         = nombre
        config.color_primario = color_primario
        config.save(update_fields=["nombre", "color_primario"])
        return Response({"mensaje": "Configuración guardada correctamente."})


# =====================================================
# Panel de administración — editar config
# =====================================================
def config_panel(request):
    if request.session.get("rol") != "ADMIN":
        return redirect("usuarios:login")

    config = ConfigInstituto.get()

    if request.method == "POST":
        nombre         = request.POST.get("nombre", "").strip()
        color_primario = request.POST.get("color_primario", "").strip()

        # Validar color hex
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color_primario):
            messages.error(request, "Color inválido. Debe ser un hexadecimal, ej: #053D4E")
        elif not nombre:
            messages.error(request, "El nombre no puede estar vacío.")
        else:
            config.nombre         = nombre
            config.color_primario = color_primario
            config.save(update_fields=["nombre", "color_primario"])
            messages.success(request, "Configuración guardada correctamente.")
            return redirect("config:panel")

    return render(request, "config/panel.html", {"config": config})