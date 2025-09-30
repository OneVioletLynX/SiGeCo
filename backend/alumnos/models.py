from django.db import models

class Alumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)

    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    dni = models.IntegerField()
    email = models.EmailField(unique=True)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    telefono = models.PositiveIntegerField(default=0)
    telefono_respaldo = models.PositiveIntegerField(default=0)
    inscripcion = models.DateField(auto_now_add=True)
    fecha_nacimiento = models.DateField()

