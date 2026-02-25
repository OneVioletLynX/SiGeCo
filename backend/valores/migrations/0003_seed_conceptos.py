from django.db import migrations

def crear_conceptos(apps, schema_editor):
    Concepto = apps.get_model("valores", "Concepto")

    Concepto.objects.get_or_create(
        id_concepto=1,
        defaults={"descripcion": "Cuota Mensual"}
    )

    Concepto.objects.get_or_create(
        id_concepto=2,
        defaults={"descripcion": "Inscripción"}
    )


def eliminar_conceptos(apps, schema_editor):
    Concepto = apps.get_model("valores", "Concepto")
    Concepto.objects.filter(id_concepto__in=[1, 2]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('valores', '0002_alter_valor_fecha_fin_alter_valor_fecha_inicio'),  # ← dejá la que ya aparece
    ]

    operations = [
        migrations.RunPython(crear_conceptos, eliminar_conceptos),
    ]