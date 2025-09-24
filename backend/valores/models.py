from django.db import models

class Valor(models.Model):
    id_carrera = models.PositiveIntegerField()
    id_concepto = models.PositiveIntegerField()
    modificacion = models.DateTimeField(auto_now_add=True)
    importe = models.IntegerField()

class Concepto(models.Model):
    descripcion = models.CharField(max_length=50, null=True, blank=True)