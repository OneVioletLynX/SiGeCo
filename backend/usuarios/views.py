from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import json

from .models import Usuario, ROLES
from backend.permisos import get_permisos
from backend.permissions import TienePermisoRol
from auditoria.models import registrar

# Intentos máximos de login por IP antes de bloquear
MAX_INTENTOS  = 5
BLOQUEO_SEG   = 300  # 5 minutos


# ========================================================
# API LOGIN con rate limiting por IP
# ========================================================
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
    cache_key = f"login_intentos_{ip}"
    intentos  = cache.get(cache_key, 0)

    if intentos >= MAX_INTENTOS:
        return JsonResponse(
            {"error": "Demasiados intentos fallidos. Intentá en 5 minutos."},
            status=429
        )

    try:
        data     = json.loads(request.body)
        username = data.get("username", "").strip()
        password = data.get("password", "")
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if not username or not password:
        return JsonResponse({"error": "Usuario y contraseña requeridos"}, status=400)

    try:
        usuario = Usuario.objects.get(username__iexact=username)
    except Usuario.DoesNotExist:
        # Incrementar intentos aunque el usuario no exista
        cache.set(cache_key, intentos + 1, BLOQUEO_SEG)
        return JsonResponse({"error": "Usuario o contraseña incorrectos"}, status=401)

    raw_pass = usuario.password_hash
    if raw_pass.startswith("pbkdf2_"):
        valido = check_password(password, raw_pass)
    else:
        valido = (password == raw_pass)
        if valido:
            usuario.password_hash = make_password(password)
            usuario.save(update_fields=["password_hash"])

    if not valido:
        cache.set(cache_key, intentos + 1, BLOQUEO_SEG)
        return JsonResponse({"error": "Usuario o contraseña incorrectos"}, status=401)

    # Login exitoso → limpiar contador de intentos
    cache.delete(cache_key)

    refresh = RefreshToken()
    refresh["usuario_id"]     = usuario.id
    refresh["usuario_nombre"] = usuario.nombre
    refresh["rol"]            = usuario.rol
    refresh["permisos"]       = get_permisos(usuario.rol)

    return JsonResponse({
        "status":   "ok",
        "rol":      usuario.rol,
        "nombre":   usuario.nombre,
        "permisos": get_permisos(usuario.rol),
        "access":   str(refresh.access_token),
        "refresh":  str(refresh),
    })


# ========================================================
# LOGIN HTML (admin backend :8000)
# ========================================================
def login_view(request):
    if request.session.get("usuario_id"):
        if request.session.get("rol") == "ADMIN":
            return redirect("usuarios:admin_dashboard")
        return redirect("http://127.0.0.1:8001/inicio")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")
        print("USERNAME:", username)
        print("PASSWORD:", password[:3])
        try:
            usuario = Usuario.objects.get(username__iexact=username)
            print("USUARIO ENCONTRADO:", usuario.rol)
            print("CHECK:", check_password(password, usuario.password_hash))
            if check_password(password, usuario.password_hash):
                request.session["usuario_id"]     = usuario.id
                request.session["usuario_nombre"] = usuario.nombre
                request.session["rol"]            = usuario.rol
                if usuario.rol == "ADMIN":
                    return redirect("usuarios:admin_dashboard")
                else:
                    return redirect("http://127.0.0.1:8001/inicio")
            messages.error(request, "Contraseña incorrecta")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    return render(request, "usuarios/login.html")


# ========================================================
# LOGOUT
# ========================================================
def logout_view(request):
    request.session.flush()
    return redirect("http://127.0.0.1:8001/")


# ========================================================
# ADMIN DASHBOARD
# ========================================================
def admin_dashboard(request):
    if request.session.get("rol") != "ADMIN":
        return redirect("usuarios:login")

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "crear":
            nombre   = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            username = request.POST.get("username", "").strip().lower()
            password = request.POST.get("password")
            rol      = request.POST.get("rol", "SECRETARIA")

            if Usuario.objects.filter(username__iexact=username).exists():
                messages.error(request, f"El usuario '{username}' ya existe.")
            else:
                Usuario.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    username=username,
                    password_hash=make_password(password),
                    rol=rol,
                )
                messages.success(request, f"Usuario '{username}' creado como {rol}.")

        elif accion == "editar":
            user_id  = request.POST.get("user_id")
            usuario  = get_object_or_404(Usuario, pk=user_id)
            usuario.nombre   = request.POST.get("nombre")
            usuario.apellido = request.POST.get("apellido")
            usuario.username = request.POST.get("username", "").strip().lower()
            usuario.rol      = request.POST.get("rol", usuario.rol)
            new_pass = request.POST.get("password")
            if new_pass:
                usuario.password_hash = make_password(new_pass)
            usuario.save()
            messages.success(request, "Usuario actualizado.")

        elif accion == "eliminar":
            user_id = request.POST.get("user_id")
            usuario = get_object_or_404(Usuario, pk=user_id)
            usuario.delete()
            messages.success(request, "Usuario eliminado.")

        return redirect("usuarios:admin_dashboard")

    from auditoria.models import RegistroAuditoria
    from config.models import ConfigInstituto
    import re as _re

    # Config POST
    if request.method == "POST" and request.POST.get("accion") == "config":
        nombre         = request.POST.get("nombre", "").strip()
        color_primario = request.POST.get("color_primario", "").strip()
        if not nombre:
            messages.error(request, "El nombre no puede estar vacío.")
        elif not _re.match(r'^#[0-9A-Fa-f]{6}$', color_primario):
            messages.error(request, "Color inválido. Debe ser hexadecimal, ej: #053D4E")
        else:
            cfg = ConfigInstituto.get()
            cfg.nombre         = nombre
            cfg.color_primario = color_primario
            cfg.save(update_fields=["nombre", "color_primario"])
            messages.success(request, "Configuración guardada correctamente.")
        return redirect("usuarios:admin_dashboard")

    usuarios = Usuario.objects.exclude(rol="ADMIN").order_by("-creado")

    # Última actividad por usuario
    usuarios_data = []
    for u in usuarios:
        ultimo = RegistroAuditoria.objects.filter(usuario_id=u.id).order_by('-fecha').first()
        usuarios_data.append({"usuario": u, "ultima_actividad": ultimo})

    # Feed de actividad reciente (últimas 20)
    actividad_reciente = RegistroAuditoria.objects.select_related().order_by('-fecha')[:20]

    # Config del instituto
    config = ConfigInstituto.get()

    return render(request, "usuarios/admin_dashboard.html", {
        "usuarios_data":     usuarios_data,
        "roles":             ROLES,
        "actividad_reciente": actividad_reciente,
        "config":            config,
    })


# ========================================================
# API REST — Gestión de usuarios (requiere JWT + rol ADMIN)
# ========================================================
class EsAdmin(IsAuthenticated):
    message = "Solo los administradores pueden acceder a esta sección."

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and getattr(request.user, 'rol', None) == 'ADMIN'
        )


class UsuarioAPIList(APIView):
    permission_classes = [EsAdmin]

    def get(self, request):
        usuarios = Usuario.objects.all().order_by("-creado")
        data = [
            {
                "id":       u.id,
                "nombre":   u.nombre,
                "apellido": u.apellido,
                "username": u.username,
                "email":    u.email,
                "rol":      u.rol,
                "creado":   u.creado.strftime("%d/%m/%Y") if u.creado else "",
            }
            for u in usuarios
        ]
        return Response(data)

    def post(self, request):
        nombre   = request.data.get("nombre", "").strip()
        apellido = request.data.get("apellido", "").strip()
        username = request.data.get("username", "").strip().lower()
        password = request.data.get("password", "")
        rol      = request.data.get("rol", "SECRETARIA")
        email    = request.data.get("email", "").strip() or None

        roles_validos = [r[0] for r in ROLES]
        if not nombre or not apellido or not username or not password:
            return Response({"error": "Campos requeridos: nombre, apellido, username, password."}, status=400)
        if rol not in roles_validos:
            return Response({"error": "Rol inválido."}, status=400)
        if Usuario.objects.filter(username__iexact=username).exists():
            return Response({"error": f"El usuario '{username}' ya existe."}, status=400)

        usuario = Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            username=username,
            email=email,
            password_hash=make_password(password),
            rol=rol,
        )
        registrar(request, 'ALTA', 'usuario',
                  f"Alta de usuario: {username} ({rol})", usuario.id)
        return Response({"id": usuario.id, "mensaje": f"Usuario '{username}' creado."}, status=201)


class UsuarioAPIDetail(APIView):
    permission_classes = [EsAdmin]

    def get_object(self, pk):
        return get_object_or_404(Usuario, pk=pk)

    def put(self, request, pk):
        usuario  = self.get_object(pk)
        nombre   = request.data.get("nombre", usuario.nombre).strip()
        apellido = request.data.get("apellido", usuario.apellido).strip()
        username = request.data.get("username", usuario.username).strip().lower()
        rol      = request.data.get("rol", usuario.rol)
        email    = request.data.get("email", usuario.email or "").strip() or None
        password = request.data.get("password", "")

        roles_validos = [r[0] for r in ROLES]
        if rol not in roles_validos:
            return Response({"error": "Rol inválido."}, status=400)
        if (
            usuario.username != username
            and Usuario.objects.filter(username__iexact=username).exists()
        ):
            return Response({"error": f"El usuario '{username}' ya existe."}, status=400)

        usuario.nombre   = nombre
        usuario.apellido = apellido
        usuario.username = username
        usuario.rol      = rol
        usuario.email    = email
        if password:
            usuario.password_hash = make_password(password)
        usuario.save()
        registrar(request, 'MODIFICACION', 'usuario',
                  f"Modificación de usuario: {usuario.username}", pk)
        return Response({"mensaje": "Usuario actualizado."})

    def delete(self, request, pk):
        usuario = self.get_object(pk)
        if usuario.rol == 'ADMIN':
            return Response({"error": "No podés eliminar a un administrador."}, status=400)
        username_guardado = usuario.username
        usuario.delete()
        registrar(request, 'BAJA', 'usuario',
                  f"Eliminación de usuario: {username_guardado}", pk)
        return Response({"mensaje": "Usuario eliminado."}, status=204)