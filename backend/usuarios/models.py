from django.db import models
from django.utils import timezone


# Roles disponibles en el sistema.
# Para agregar uno nuevo, solo agregarlo acá y en PERMISOS_POR_ROL de permisos.py
ROL_ADMIN       = 'ADMIN'
ROL_SECRETARIA  = 'SECRETARIA'
ROL_COORDINADOR = 'COORDINADOR'

ROLES = [
    (ROL_ADMIN,       'Administrador'),
    (ROL_SECRETARIA,  'Secretaria'),
    (ROL_COORDINADOR, 'Coordinador'),
]


class Usuario(models.Model):

    nombre   = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email    = models.EmailField(max_length=254, unique=True, blank=True, null=True)

    password_hash = models.CharField(max_length=128)

    rol = models.CharField(
        max_length=40,
        choices=ROLES,
        default=ROL_SECRETARIA,
    )

    creado      = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table            = 'usuarios_usuario'
        managed             = False
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.nombre} {self.apellido}) — {self.rol}"

    @property
    def es_admin(self):
        return self.rol == ROL_ADMIN

    # Propiedades requeridas por Django REST Framework
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return True