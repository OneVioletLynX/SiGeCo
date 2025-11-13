from django.db import models
from alumnos.models import Alumno
from carreras.models import Carrera

class Mensaje(models.Model):
    TIPO_ENVIO_CHOICES = [
        ('correo', 'Correo'),
        ('whatsapp', 'WhatsApp'),
    ]

    ESTADO_ENVIO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('fallido', 'Fallido'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    tipo_envio = models.CharField(max_length=20, choices=TIPO_ENVIO_CHOICES)

    # Nuevas columnas
    en_programado = models.BooleanField(default=False)
    estado_envio = models.CharField(
        max_length=20,
        choices=ESTADO_ENVIO_CHOICES,
        default='pendiente'
    )

    # Relaciones con usuarios (solo guardamos IDs)
    destino_deudores = models.JSONField(default=list, blank=True)   # lista de IDs de alumnos
    destino_carrera = models.JSONField(default=list, blank=True)    # lista de IDs de carreras

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mensajes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    # Método opcional para enviar correo si tipo_envio = 'correo'
    def enviar_email(self):
        if self.tipo_envio != 'correo':
            return

        from django.core.mail import send_mail

        # Ejemplo: emails vacíos por ahora, se debe implementar fetch de alumnos/carreras por ID
        emails = []

        if emails:
            send_mail(
                subject=self.titulo,
                message=self.descripcion,
                from_email=None,
                recipient_list=emails,
                fail_silently=False
            )
            self.estado_envio = 'enviado'
            self.save()
