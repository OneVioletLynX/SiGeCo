from django.db import models

# Importación de Alumno con manejo de contextos
try:
    from alumnos.models import Alumno
except ImportError:
    from backend.alumnos.models import Alumno

# 1. MODELO ESTADO
class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'carreras_estado'
        verbose_name = "Estado"
        verbose_name_plural = "Estados"

    def __str__(self):
        return self.descripcion

# 2. MODELO CARRERA
class Carrera(models.Model):
    id_carrera = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#1E3A8A")
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE, default=1)
    
    class Meta:
        db_table = 'carreras_carrera'
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self):
        return self.descripcion

# 3. MODELO CURSADA (Solución al error 1054)
class CarreraCursada(models.Model):
    # TRUCO: Le ponemos primary_key=True a alumno. 
    # Esto evita que Django busque la columna 'id' que no existe.
    alumno = models.ForeignKey(
        Alumno, 
        on_delete=models.CASCADE, 
        related_name='carreras_cursadas',
        primary_key=True 
    )
    
    carrera = models.ForeignKey(
        Carrera, 
        on_delete=models.CASCADE, 
        related_name="carreras_cursadas"
    )
    
    id_estado = models.ForeignKey(
        Estado, 
        on_delete=models.CASCADE, 
        default=1
    )

    class Meta:
        db_table = "carreras_cursadas"
        managed = False  # IMPORTANTE: Le decimos a Django que no toque la estructura de esta tabla
        verbose_name = "Cursada"
        verbose_name_plural = "Cursadas"
        unique_together = (('alumno', 'carrera'),)