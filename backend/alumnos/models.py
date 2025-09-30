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
    legajo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=50,  default='Pendiente')
    apellido = models.CharField(max_length=50, default='Pendiente')
    fecha_nac = models.DateField(blank=True, null=True)
    # si hoy lo tenés como IntegerField, ver nota de DNI abajo
    dni = models.CharField(max_length=8, unique=True)  # recomendado
    ciudad = models.CharField(max_length=50, blank=True)
    direccion = models.CharField(max_length=50, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    descripcion = models.CharField(max_length=300, blank=True)
    anio_ingreso = models.PositiveIntegerField(
        blank=True, null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'
