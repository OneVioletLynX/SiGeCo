from django.db import models
try:
    from carreras.models import Carrera
except ImportError:
    from backend.carreras.models import Carrera


class Concepto(models.Model):
    id_concepto = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.descripcion or ""


class Valor(models.Model):
    id_valor = models.AutoField(primary_key=True)
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='valores')
    id_concepto = models.ForeignKey(Concepto, on_delete=models.CASCADE, related_name='valores')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    importe = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'valores_valor'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.id_carrera.descripcion} - {self.id_concepto.descripcion} (${self.importe})"
