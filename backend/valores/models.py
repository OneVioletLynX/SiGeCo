from django.db import models
from carreras.models import Carrera

class Concepto(models.Model):
    id_concepto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, null=True, blank=True)

class Valor(models.Model):
    id_valor = models.AutoField(primary_key=True)
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    id_concepto = models.ForeignKey(Concepto, on_delete=models.CASCADE)
    modificacion = models.DateTimeField(auto_now_add=True)
    importe = models.IntegerField()

