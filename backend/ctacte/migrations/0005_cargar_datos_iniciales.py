from django.db import migrations

def cargar_datos_ctacte(apps, schema_editor):
    MesPago = apps.get_model('ctacte', 'MesPago')
    MetodoPago = apps.get_model('ctacte', 'MetodoPago')

    meses = [

        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
        (13, 'Inscripcion')
    ]

    for id_mes, descripcion in meses:
        MesPago.objects.update_or_create(
            id_mes=id_mes,
            defaults={'descripcion': descripcion}
        )

    metodos = [
        (1, 'Efectivo'),
        (2, 'Transferencia'),
    ]

    for id_metodo, descripcion in metodos:
        MetodoPago.objects.update_or_create(
            id_metodo_pago=id_metodo,
            defaults={'descripcion': descripcion}
        )


class Migration(migrations.Migration):

    dependencies = [
        ('ctacte', '0004_alter_pago_table'),
    ]

    operations = [
        migrations.RunPython(cargar_datos_ctacte),
    ]