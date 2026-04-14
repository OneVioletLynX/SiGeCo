from django.db import models


class MesPago(models.Model):
    id_mes = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = "ctacte_mespago"
        verbose_name = "Mes de Pago"
        verbose_name_plural = "Meses de Pago"

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = "ctacte_metodopago"
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return self.descripcion


class Pago(models.Model):

    id_pago = models.AutoField(primary_key=True)

    id_alumno = models.ForeignKey(
        "alumnos.Alumno",
        on_delete=models.CASCADE,
        related_name="pagos"
    )

    fecha_pago = models.DateTimeField(
        null=True,
        blank=True
    )

    importe_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    id_metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name="pagos"
    )

    class Meta:
        db_table = "ctacte_pago"
        ordering = ["-fecha_pago"]
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        alumno_nombre = self.id_alumno.nombre if self.id_alumno else "Alumno"
        return f"Pago #{self.id_pago} - {alumno_nombre} - ${self.importe_total}"


class PagoDetalle(models.Model):

    id_detalle = models.AutoField(primary_key=True)

    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    carrera = models.ForeignKey(
        "carreras.Carrera",
        on_delete=models.PROTECT,
        related_name="pagos_detalle"
    )

    mes = models.ForeignKey(
        MesPago,
        on_delete=models.PROTECT,
        related_name="detalles_pago"
    )

    anio_pago = models.PositiveIntegerField()

    id_concepto = models.ForeignKey(
        "valores.Concepto",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "pago_detalle"
        # La unicidad es por pago (que pertenece a un alumno), carrera, mes y año.
        # Esto impide duplicar el mismo mes/carrera/año dentro del mismo pago,
        # y la validación en RegistrarPago impide duplicarlo entre pagos distintos.
        unique_together = [["pago", "carrera", "mes", "anio_pago"]]
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"

    def __str__(self):
        return f"{self.carrera.descripcion} - {self.mes.descripcion} {self.anio_pago}"


class EstadoCuota(models.Model):

    id_estado = models.AutoField(primary_key=True)

    descripcion = models.CharField(
        max_length=30,
        unique=True
    )

    class Meta:
        db_table = "ctacte_estado_cuota"

    def __str__(self):
        return self.descripcion


class Cuota(models.Model):

    id_cuota = models.AutoField(primary_key=True)

    alumno = models.ForeignKey(
        "alumnos.Alumno",
        on_delete=models.CASCADE,
        related_name="cuotas"
    )

    carrera = models.ForeignKey(
        "carreras.Carrera",
        on_delete=models.CASCADE
    )

    mes = models.ForeignKey(
        MesPago,
        on_delete=models.PROTECT
    )

    anio = models.PositiveIntegerField()

    estado = models.ForeignKey(
        EstadoCuota,
        on_delete=models.PROTECT
    )

    importe = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    class Meta:
        db_table = "ctacte_cuota"
        unique_together = [["alumno", "carrera", "mes", "anio"]]

    def __str__(self):
        return f"{self.alumno} - {self.mes.descripcion} {self.anio}"