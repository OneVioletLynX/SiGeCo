from django.db import models
from django.conf import settings

class MesPago(models.Model):
    id_mes = models.AutoField(primary_key=True, db_column='id_mes')
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'mes_pago'
        ordering = ['id_mes']

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True, db_column='id_metodo_pago')
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'metodos_pagos'
        ordering = ['id_metodo_pago']

    def __str__(self):
        return self.descripcion


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True, db_column='id_pago')
    alumno = models.ForeignKey('alumnos.Alumno', on_delete=models.CASCADE,
                               db_column='id_alumno', related_name='pagos')
    fecha_pago = models.DateTimeField()
    importe_total = models.DecimalField(max_digits=12, decimal_places=2, db_column='importe_total')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, db_column='id_metodo_pago')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_column='id_usuario')

    class Meta:
        db_table = 'pago'
        ordering = ['-fecha_pago', '-id_pago']

    def __str__(self):
        return f'Pago {self.id_pago} - {self.alumno} - {self.importe_total}'


class PagoDetalle(models.Model):
    id_detalle = models.AutoField(primary_key=True, db_column='id_detalle')  # PK simple
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, db_column='id_pago', related_name='detalles')
    mes = models.ForeignKey(MesPago, on_delete=models.PROTECT, db_column='id_mes')
    importe = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'pago_detalle'
        constraints = [
            models.UniqueConstraint(fields=['pago', 'mes'], name='uq_pago_mes')  # (pago, mes) único
        ]

    def __str__(self):
        return f'Detalle {self.id_detalle} - Pago {self.pago_id} - {self.mes} - {self.importe}'






