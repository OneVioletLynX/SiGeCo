from django.db import models
from django.utils import timezone

class Usuario(models.Model):
    # Mapeo exacto a tu tabla
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    
    # En Django se llama password, aquí lo mapeamos a tu columna 'password_hash'
    password = models.CharField(max_length=128, db_column='password_hash')
    
    # Usaremos el token para definir el ROL por ahora si no quieres cambiar la estructura
    # 'ADMIN' = Administrador, cualquier otra cosa = Normal
    token = models.CharField(max_length=40, unique=True, default='normal') 
    
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'usuarios_usuario'
        managed = False # Django no tocará esta tabla
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_admin(self):
        return self.token == 'ADMIN'