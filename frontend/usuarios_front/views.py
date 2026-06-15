from django.shortcuts import render

def login_view(request):
    return render(request, "login.html")

def admin_usuarios(request):
    return render(request, "usuarios_front/admin_usuarios.html")

def admin_config(request):
    return render(request, "usuarios_front/admin_config.html")