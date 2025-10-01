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

    # si hoy lo tenés como IntegerField, ver nota de DNI abajo
    anio_ingreso = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'
