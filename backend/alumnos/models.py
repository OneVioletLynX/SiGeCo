from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Alumno(models.Model):
    id_alumno = models.AutoField(primary_key=True)
    legajo = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100, null=True, blank=True)
    apellido = models.CharField(max_length=100, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    dni = models.IntegerField()
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    
    # Campo principal de contacto
    telefono = models.PositiveIntegerField(default=0)
    
    # --- CAMPO TELEFONO RESPALDO (REQUERIDO POR LA DB Y SERIALIZER) ---
    # telefono_respaldo = models.PositiveIntegerField(
    #     default=0,
    #     verbose_name="Teléfono Respaldo"
    # )
    # -----------------------------------------------------------------
    
    email = models.EmailField(unique=True)
    
    # Nota: Tu DB parece usar 'inscripcion' como fecha, no como auto_now_add
    inscripcion = models.DateField() 
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)
    
    anio_ingreso = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
    )

    class Meta:
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'