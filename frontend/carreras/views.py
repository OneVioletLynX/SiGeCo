from django.shortcuts import render, redirect


def carreras(request):
    return render(request, 'carreras/index.html')