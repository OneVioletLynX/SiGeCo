from django.db import models


class Concepto(models.Model):

    id_concepto = models.AutoField(primary_key=True)

    descripcion = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "valores_concepto"
        verbose_name = "Concepto de Valor"
        verbose_name_plural = "Conceptos de Valor"

    def __str__(self):
        return self.descripcion or ""


class Valor(models.Model):

    id_valor = models.AutoField(primary_key=True)

    id_carrera = models.ForeignKey(
        "carreras.Carrera",
        on_delete=models.CASCADE,
        related_name="valores"
    )

    id_concepto = models.ForeignKey(
        Concepto,
        on_delete=models.CASCADE,
        related_name="valores"
    )

    fecha_inicio = models.DateField()

    fecha_fin = models.DateField(
        null=True,
        blank=True
    )

    importe = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        db_table = "valores_valor"
        verbose_name = "Valor"
        verbose_name_plural = "Valores"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        carrera = self.id_carrera.descripcion if self.id_carrera else ""
        concepto = self.id_concepto.descripcion if self.id_concepto else ""
        return f"{carrera} - {concepto} (${self.importe})"