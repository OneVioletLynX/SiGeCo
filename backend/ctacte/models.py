from django.db import models
from django.conf import settings
from alumnos.models import Alumno

class MesPago(models.Model):
    id_mes = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.descripcion


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField()
    importe_total = models.DecimalField(max_digits=12, decimal_places=2)
    id_metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    #id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f'Pago {self.pago} - {self.alumno} - {self.importe_total}'



class PagoDetalle(models.Model):
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
    mes = models.ForeignKey(MesPago, on_delete=models.CASCADE)
    importe = models.DecimalField(max_digits=12, decimal_places=2)

    pk = models.CompositePrimaryKey("pago", "mes")

    class Meta:
        db_table = 'pago_detalle'






