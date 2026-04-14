from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import json

from .models import Usuario, ROLES
from backend.permisos import get_permisos

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
        return redirect("mensajes:index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        try:
            usuario = Usuario.objects.get(username__iexact=username)
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
    return redirect("usuarios:login")


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

    usuarios = Usuario.objects.exclude(rol="ADMIN").order_by("-creado")
    return render(request, "usuarios/admin_dashboard.html", {
        "usuarios": usuarios,
        "roles":    ROLES,
    })