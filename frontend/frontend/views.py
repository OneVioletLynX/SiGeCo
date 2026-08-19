from django.shortcuts import render

def home(request):
    return render(request, "shared/home.html")

def nosotros(request):
    return render(request, "shared/nosotros.html")

