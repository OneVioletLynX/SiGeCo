from django.db import models
from django.conf import settings

# --- IMPORTACIONES ---
try:
    # Cuando corre el backend directo
    from alumnos.models import Alumno
    from valores.models import Concepto
except ImportError:
    # Cuando se importa desde otro contexto o script
    from backend.alumnos.models import Alumno
    from backend.valores.models import Concepto


class MesPago(models.Model):
    id_mes = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'ctacte_mespago'   # cambiar si tu tabla se llama ctacte_mes_pago u otro
        verbose_name = "Mes de Pago"
        verbose_name_plural = "Meses de Pago"

    def __str__(self):
        return self.descripcion


class MetodoPago(models.Model):
    id_metodo_pago = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'ctacte_metodopago'  # cambiar si tu tabla tiene otro nombre
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"

    def __str__(self):
        return self.descripcion


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    id_alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name='pago'
    )
    # Usé null=True para permitir flexibilidad, si prefieres que sea
    # automático al crear, usa auto_now_add=True
    fecha_pago = models.DateTimeField(null=True, blank=True)
    importe_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    id_metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name='pago'
    )
    # id_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        # Verifica si tu tabla es 'pago' o 'ctacte_pago'
        db_table = 'ctacte_pago' 
        ordering = ['-fecha_pago']
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self):
        alumno = getattr(self.id_alumno, 'nombre', 'Alumno desc.') if self.id_alumno else ''
        return f'Pago #{self.id_pago} - {alumno} - ${self.importe_total}'


class PagoDetalle(models.Model):
    # Fusioné la definición de ID explícito con los campos nuevos
    id_detalle = models.AutoField(primary_key=True)
    
    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    mes = models.ForeignKey(
        MesPago,
        on_delete=models.PROTECT,
        related_name='pagos_detalle'
    )
    # Campos que estaban en la segunda definición y son importantes
    anio_pago = models.PositiveIntegerField(null=True, blank=True) # Lo puse opcional por seguridad, quita null=True si es obligatorio
    id_concepto = models.ForeignKey(
        Concepto, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    
    importe = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'pago_detalle'
        unique_together = (('pago', 'mes'),)   # ✔ simula PK compuesta
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"

    def __str__(self):
        mes_desc = self.mes.descripcion if self.mes else ''
        return f"Detalle {self.id_detalle} - Pago {self.pago_id} - {mes_desc}"
