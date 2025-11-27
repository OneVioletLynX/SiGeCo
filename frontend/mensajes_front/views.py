from django.shortcuts import render, redirect


def mensajes(request):
    return render(request, 'mensajes/index.html')