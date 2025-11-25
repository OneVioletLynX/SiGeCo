# from django.db import models
# from django.conf import settings
# from alumnos.models import Alumno

# class MesPago(models.Model):
#     id_mes = models.AutoField(primary_key=True)
#     descripcion = models.CharField(max_length=20, unique=True)

#     def __str__(self):
#         return self.descripcion


# class MetodoPago(models.Model):
#     id_metodo_pago = models.AutoField(primary_key=True)
#     descripcion = models.CharField(max_length=20, unique=True)

#     def __str__(self):
#         return self.descripcion


# class Pago(models.Model):
#     id_pago = models.AutoField(primary_key=True)
#     id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
#     fecha_pago = models.DateTimeField()
#     importe_total = models.DecimalField(max_digits=12, decimal_places=2)
#     id_metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
#     #id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

#     def __str__(self):
#         return f'Pago {self.pago} - {self.alumno} - {self.importe_total}'



# class PagoDetalle(models.Model):
#     pago = models.ForeignKey(Pago, on_delete=models.CASCADE)
#     mes = models.ForeignKey(MesPago, on_delete=models.CASCADE)
#     importe = models.DecimalField(max_digits=12, decimal_places=2)

#     pk = models.CompositePrimaryKey("pago", "mes")

#     class Meta:
#         db_table = 'pago_detalle'


#NUEVO:

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
        db_table = 'ctacte_mespago'   # cambiar si tu tabla se llama ctacte_mes_pago u otro
        verbose_name = "Mes de Pago"
        verbose_name_plural = "Meses de Pago"

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'ctacte_metodopago'  # cambiar si tu tabla tiene otro nombre
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return self.descripcion


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name='pago'
    )
    fecha_pago = models.DateTimeField(null=True, blank=True)
    importe_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    id_metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name='pago'
    )
    # id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'ctacte_pago' 
        ordering = ['-fecha_pago']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        alumno = getattr(self.id_alumno, 'nombre', '') if self.id_alumno else ''
        return f'Pago #{self.id_pago} - {alumno} - {self.importe_total}'


class PagoDetalle(models.Model):
    id = models.AutoField(primary_key=True)   # ✔ PK limpia, sin problemas

    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    mes = models.ForeignKey(
        MesPago,
        on_delete=models.CASCADE,
        related_name='pagos_detalle'
    )
    importe = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'pago_detalle'
        unique_together = (('pago', 'mes'),)   # ✔ simula PK compuesta
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"

    def __str__(self):
        mes_desc = self.mes.descripcion if self.mes else ''
        return f'Pago #{self.pago_id} - {mes_desc} - {self.importe}'



