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
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, default=1)
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=1)

    pk = models.CompositePrimaryKey("alumno", "carrera")

    class Meta:
        db_table = "carreras_cursadas"