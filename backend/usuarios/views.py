from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from .models import Usuario
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
    except:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    try:
        usuario = Usuario.objects.get(email=email)

        raw_pass = usuario.password

        # Verificar password
        if raw_pass.startswith("pbkdf2_"):
            valido = check_password(password, raw_pass)
        else:
            valido = (password == raw_pass)
            if valido:
                usuario.password = make_password(password)
                usuario.save(update_fields=["password"])

        if not valido:
            return JsonResponse({"error": "Contraseña incorrecta"}, status=401)

        # Crear sesión
        request.session['usuario_id'] = usuario.id
        request.session['usuario_nombre'] = usuario.nombre
        request.session['rol'] = 'ADMIN' if usuario.token == 'ADMIN' else 'NORMAL'

        return JsonResponse({
            "status": "ok",
            "rol": "ADMIN" if usuario.token == "ADMIN" else "NORMAL"
        })

    except Usuario.DoesNotExist:
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)

# ========================================================
# 1. VISTA DE INICIO DE SESIÓN (LOGIN)
# ========================================================
def login_view(request):
    # Si el usuario ya tiene sesión activa, lo redirigimos
    if request.session.get('usuario_id'):
        if request.session.get('rol') == 'ADMIN':
            return redirect('usuarios:admin_dashboard')
        return redirect('mensajes:index')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            usuario = Usuario.objects.get(email=email)
            
            # Verificamos la contraseña hasheada
            if check_password(password, usuario.password):
                # --- CREAR SESIÓN MANUAL ---
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nombre'] = usuario.nombre
                # Definir rol basado en el token
                request.session['rol'] = 'ADMIN' if usuario.token == 'ADMIN' else 'NORMAL'

                # Redirección según rol
                if usuario.token == 'ADMIN':
                    return redirect('usuarios:admin_dashboard')
                else:
                    return redirect('mensajes:index')
            else:
                messages.error(request, "Contraseña incorrecta")
        
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")

    return render(request, 'usuarios/login.html')


# ========================================================
# 2. VISTA DE CIERRE DE SESIÓN (LOGOUT)
# ========================================================
def logout_view(request):
    request.session.flush() # Elimina todos los datos de la sesión
    return redirect('usuarios:login')


# ========================================================
# 3. DASHBOARD DE ADMINISTRADOR (GRILLA + MODALES)
# ========================================================
def admin_dashboard(request):
    # 1. Seguridad: Solo ADMIN puede entrar aquí
    if request.session.get('rol') != 'ADMIN':
        return redirect('usuarios:login')

    # 2. Procesar Acciones (POST)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        # --- CREAR USUARIO ---
        if accion == 'crear':
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, "El email ya está registrado.")
            else:
                Usuario.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    password=make_password(password), # IMPORTANTE: Hashear password
                    token=f"user_{email}" # Generar un token simple por defecto
                )
                messages.success(request, "Usuario creado exitosamente.")

        # --- EDITAR USUARIO ---
        elif accion == 'editar':
            user_id = request.POST.get('user_id')
            usuario = get_object_or_404(Usuario, pk=user_id)
            
            usuario.nombre = request.POST.get('nombre')
            usuario.apellido = request.POST.get('apellido')
            usuario.email = request.POST.get('email')
            
            # Solo actualizamos password si escribieron algo nuevo
            new_pass = request.POST.get('password')
            if new_pass:
                usuario.password = make_password(new_pass)
            
            usuario.save()
            messages.success(request, "Usuario actualizado correctamente.")

        # --- ELIMINAR USUARIO ---
        elif accion == 'eliminar':
            user_id = request.POST.get('user_id')
            usuario = get_object_or_404(Usuario, pk=user_id)
            usuario.delete()
            messages.success(request, "Usuario eliminado.")

        # Recargamos la página para ver cambios y limpiar el formulario
        return redirect('usuarios:admin_dashboard')

    # 3. GET: Listar usuarios (Excluyendo al Admin principal)
    usuarios = Usuario.objects.exclude(token='ADMIN').order_by('-creado')
    
    return render(request, 'usuarios/admin_dashboard.html', {'usuarios': usuarios})