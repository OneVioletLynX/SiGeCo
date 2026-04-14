from django.db import migrations


class Migration(migrations.Migration):
    """
    Corrige el unique_together de PagoDetalle.

    ANTES: [["carrera", "mes", "anio_pago"]]
    → Impedía que DOS ALUMNOS distintos pagaran el mismo mes/carrera/año.

    AHORA: [["pago", "carrera", "mes", "anio_pago"]]
    → La restricción es dentro del mismo pago (que pertenece a un alumno).
    La validación de duplicados entre pagos distintos del mismo alumno
    se maneja en la vista RegistrarPago antes de tocar la BD.
    """

    dependencies = [
        ('ctacte', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pagodetalle',
            unique_together={('pago', 'carrera', 'mes', 'anio_pago')},
        ),
    ]