from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from .models import Usuario
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# ========================================================
# API LOGIN (fetch frontend)
# ========================================================
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()
        password = data.get("password", "")
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    try:
        # IGNORA MAYÚSCULAS EN EMAIL
        usuario = Usuario.objects.get(email__iexact=email)

        raw_pass = usuario.password_hash

        # Verificar password
        if raw_pass.startswith("pbkdf2_"):
            valido = check_password(password, raw_pass)
        else:
            # texto plano
            valido = (password == raw_pass)
            if valido:
                usuario.password_hash = make_password(password)
                usuario.save(update_fields=["password_hash"])

        if not valido:
            return JsonResponse({"error": "Contraseña incorrecta"}, status=401)

        # Crear sesión
        request.session['usuario_id'] = usuario.id
        request.session['usuario_nombre'] = usuario.nombre
        request.session['rol'] = 'ADMIN' if usuario.token == 'ADMIN' else 'NORMAL'

        return JsonResponse({
            "status": "ok",
            "rol": request.session['rol']
        })

    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)


# ========================================================
# LOGIN NORMAL (form HTML)
# ========================================================
def login_view(request):

    if request.session.get('usuario_id'):
        if request.session.get('rol') == 'ADMIN':
            return redirect('usuarios:admin_dashboard')
        return redirect('mensajes:index')

    if request.method == 'POST':
        email = request.POST.get('email', "").strip()
        password = request.POST.get('password')

        try:
            # IGNORA MAYÚSCULAS
            usuario = Usuario.objects.get(email__iexact=email)

            if check_password(password, usuario.password_hash):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre
                request.session['rol'] = 'ADMIN' if usuario.token == 'ADMIN' else 'NORMAL'

                if usuario.token == 'ADMIN':
                    return redirect('usuarios:admin_dashboard')
                else:
                    return redirect('http://127.0.0.1:8001/inicio')

            messages.error(request, "Contraseña incorrecta")

        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    return render(request, 'usuarios/login.html')


# ========================================================
# LOGOUT
# ========================================================
def logout_view(request):
    request.session.flush()
    return redirect('usuarios:login')


# ========================================================
# ADMIN DASHBOARD
# ========================================================
def admin_dashboard(request):
    if request.session.get('rol') != 'ADMIN':
        return redirect('usuarios:login')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        # CREAR
        if accion == 'crear':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email').strip()
            password = request.POST.get('password')

            if Usuario.objects.filter(email__iexact=email).exists():
                messages.error(request, "El email ya está registrado.")
            else:
                Usuario.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    password_hash=make_password(password),
                    token=f"user_{email}"
                )
                messages.success(request, "Usuario creado exitosamente.")

        # EDITAR
        elif accion == 'editar':
            user_id = request.POST.get('user_id')
            usuario = get_object_or_404(Usuario, pk=user_id)

            usuario.nombre = request.POST.get('nombre')
            usuario.apellido = request.POST.get('apellido')
            usuario.email = request.POST.get('email').strip()

            new_pass = request.POST.get('password')
            if new_pass:
                usuario.password_hash = make_password(new_pass)

            usuario.save()
            messages.success(request, "Usuario actualizado correctamente.")

        # ELIMINAR
        elif accion == 'eliminar':
            user_id = request.POST.get('user_id')
            usuario = get_object_or_404(Usuario, pk=user_id)
            usuario.delete()
            messages.success(request, "Usuario eliminado.")

        return redirect('usuarios:admin_dashboard')

    usuarios = Usuario.objects.exclude(token='ADMIN').order_by('-creado')
    return render(request, 'usuarios/admin_dashboard.html', {'usuarios': usuarios})
