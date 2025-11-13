from django.shortcuts import render
from backend.ctacte.models import MesPago, MetodoPago

def cobros(request):
    meses = MesPago.objects.all().order_by('id_mes')
    metodos = MetodoPago.objects.all().order_by('id_metodo_pago')
    return render(request, 'cobros/index.html', {'meses': meses, 'metodos': metodos})
