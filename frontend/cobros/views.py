from django.shortcuts import render, redirect


def cobros(request):
    return render(request, 'cobros/index.html')