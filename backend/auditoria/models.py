from django.db import models


class RegistroAuditoria(models.Model):
    ACCIONES = [
        ('ALTA',         'Alta'),
        ('MODIFICACION', 'Modificación'),
        ('BAJA',         'Baja'),
        ('COBRO',        'Cobro'),
    ]

    usuario_id     = models.IntegerField(null=True, blank=True)
    usuario_nombre = models.CharField(max_length=200, blank=True)
    accion         = models.CharField(max_length=20, choices=ACCIONES)
    entidad        = models.CharField(max_length=50)
    entidad_id     = models.IntegerField(null=True, blank=True)
    descripcion    = models.CharField(max_length=500)
    fecha          = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha:%d/%m/%Y %H:%M} — {self.accion} {self.entidad}: {self.descripcion}"


def registrar(request, accion, entidad, descripcion, entidad_id=None):
    uid    = getattr(request.user, 'id', None)
    nombre = ""
    if uid:
        u      = request.user
        nombre = f"{getattr(u, 'nombre', '')} {getattr(u, 'apellido', '')}".strip()
        if not nombre:
            nombre = getattr(u, 'username', '')
    try:
        RegistroAuditoria.objects.create(
            usuario_id=uid,
            usuario_nombre=nombre,
            accion=accion,
            entidad=entidad,
            entidad_id=entidad_id,
            descripcion=descripcion,
        )
    except Exception:
        pass
