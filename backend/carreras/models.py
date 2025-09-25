from django.db import models
from alumnos.models import Alumno


class Carrera(models.Model):
    id_carrera = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)

    def __str__(self):
        return self.descripcion


class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion


class CarreraCursada(models.Model):
    id_alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    id_carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("id_alumno", "id_carrera")  # PK compuesta

    def __str__(self):
        return f"{self.id_alumno} - {self.id_carrera} ({self.id_estado})"
