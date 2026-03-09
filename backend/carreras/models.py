from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Estado(models.Model):

    id_estado = models.AutoField(primary_key=True)

    descripcion = models.CharField(
        max_length=50
    )

    class Meta:
        db_table = "carreras_estado"
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.descripcion

class Carrera(models.Model):

    id_carrera = models.AutoField(primary_key=True)

    descripcion = models.CharField(
        max_length=100
    )

    color = models.CharField(
        max_length=7,
        default="#1E3A8A"
    )

    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE,
        default=1,
        related_name="carreras"
    )

    class Meta:
        db_table = "carreras_carrera"
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return self.descripcion

class CarreraCursada(models.Model):

    alumno = models.ForeignKey(
        "alumnos.Alumno",
        on_delete=models.CASCADE,
        related_name="carreras_cursadas",
        db_column="alumno_id"
    )

    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.CASCADE,
        related_name="alumnos_cursando",
        db_column="carrera_id"
    )

    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.CASCADE,
        default=1,
        db_column="id_estado_id",
        related_name="carreras_cursadas"
    )

    inscripcion = models.DateField(
        auto_now_add=True
    )

    fecha_inscripcion = models.DateTimeField(
        blank=True,
        null=True
    )

    anio_ingreso = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(2100)
        ]
    )

    class Meta:
        db_table = "carreras_cursadas"
        unique_together = [["alumno", "carrera"]]
        verbose_name = "Carrera cursada"
        verbose_name_plural = "Carreras cursadas"

    def __str__(self):
        return f"{self.alumno} - {self.carrera}"