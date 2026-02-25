from django.db import migrations

def crear_estados_iniciales(apps, schema_editor):
    Estado = apps.get_model('carreras', 'Estado')

    # Evita duplicados si ya existen
    if not Estado.objects.filter(id_estado=1).exists():
        Estado.objects.create(
            id_estado=1,
            descripcion='Activo'
        )

    if not Estado.objects.filter(id_estado=2).exists():
        Estado.objects.create(
            id_estado=2,
            descripcion='Inactivo'
        )


class Migration(migrations.Migration):

    dependencies = [
        ('carreras', '0003_carrera_id_estado'),  # 👈 reemplaza esto
    ]

    operations = [
        migrations.RunPython(crear_estados_iniciales),
    ]