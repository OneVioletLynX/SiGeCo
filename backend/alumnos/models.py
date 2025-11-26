from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# class Alumno(models.Model):
#     nombre = models.CharField(max_length=100, null=True, blank=True)
#     apellido = models.CharField(max_length=100, null=True, blank=True)
#     dni = models.IntegerField(max_length=10)
#     email = models.EmailField(unique=True)
#     ciudad = models.CharField(max_length=100)
#     direccion = models.CharField(max_length=100)
#     telefono = models.PositiveIntegerField(default='0000000000')
#     telefono_respaldo = models.PositiveIntegerField(default='0000000000')
#     inscripcion = models.DateField(auto_now_add=True)
#     fecha_nacimiento = models.DateField()


class Alumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)

    legajo = models.CharField(max_length=20, unique=True, blank=True, null=True)

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    fecha_nacimiento = models.DateField()
    dni = models.IntegerField(unique=True)

    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    numero = models.IntegerField()
    prefijo = models.IntegerField()
    telefono = models.PositiveIntegerField()

    email = models.EmailField(unique=True)

    inscripcion = models.DateField(auto_now_add=True)
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)

    anio_ingreso = models.PositiveIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"
