from django.db import models


class Alumno(models.Model):

    id_alumno = models.AutoField(primary_key=True)

    legajo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    nombre = models.CharField(
        max_length=100
    )

    apellido = models.CharField(
        max_length=100
    )

    fecha_nacimiento = models.DateField()

    dni = models.IntegerField(
        unique=True
    )

    cuit = models.CharField(
        max_length=11,
        unique=True,
        blank=True,
        null=True
    )

    ciudad = models.ForeignKey(
        "geografia.Localidad",
        on_delete=models.PROTECT,
        db_column="ciudad"
    )

    direccion = models.CharField(
        max_length=100
    )

    numero = models.IntegerField()

    piso = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )

    departamento = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    prefijo = models.IntegerField()

    telefono = models.PositiveIntegerField()

    email = models.EmailField(
        unique=True
    )

    class Meta:
        db_table = "alumnos_alumno"
        ordering = ["apellido", "nombre"]
        verbose_name = "Alumno"
        verbose_name_plural = "Alumnos"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"