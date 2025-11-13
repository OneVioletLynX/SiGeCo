from django.db import models
from django.conf import settings
# DESPUÉS (Correcto, ruta absoluta al backend)
try:
    # Cuando corre el backend (8000) y las apps están registradas como 'alumnos'
    from alumnos.models import Alumno
    from valores.models import Concepto
except ImportError:
    # Cuando corre el frontend (8001) y se importan como 'backend.alumnos'
    from backend.alumnos.models import Alumno
    from backend.valores.models import Concepto


class MesPago(models.Model):
    id_mes = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'mes_pago'

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'metodo_pago'

    def __str__(self):
        return self.descripcion


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    importe_total = models.DecimalField(max_digits=12, decimal_places=2)
    id_metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pago'

    def __str__(self):
        return f"Pago {self.id_pago} - Alumno {self.id_alumno_id} - ${self.importe_total}"


class PagoDetalle(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    pago = models.ForeignKey(Pago, related_name="detalles", on_delete=models.CASCADE)
    mes = models.ForeignKey(MesPago, on_delete=models.PROTECT)
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    anio_pago = models.PositiveIntegerField()
    id_concepto = models.ForeignKey(Concepto, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'pago_detalle'

    def __str__(self):
        return f"Detalle {self.id_detalle} - Pago {self.pago_id} - {self.mes.descripcion}"





