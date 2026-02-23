from django.db import migrations

def cargar_estados_faltantes(apps, schema_editor):
    Estado = apps.get_model('carreras', 'Estado')

    estados = [
        (3, 'Eliminado'),
        (4, 'Finalizado'),
        (5, 'Ingresante'),
    ]

    for id_estado, descripcion in estados:
        Estado.objects.update_or_create(
            id_estado=id_estado,
            defaults={'descripcion': descripcion}
        )


class Migration(migrations.Migration):

    dependencies = [
        ('carreras', '0004_auto_20260223_0936'),
    ]

    operations = [
        migrations.RunPython(cargar_estados_faltantes),
    ]