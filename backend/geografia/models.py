from django.db import models


class Provincia(models.Model):
    id_prov = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Provincias"

    def __str__(self):
        return self.nombre


class Departamento(models.Model):
    id_dpto = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(
        Provincia,
        on_delete=models.CASCADE,
        related_name="departamentos"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"


class Localidad(models.Model):
    id_loc = models.BigIntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.CASCADE,
        related_name="localidades"
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"