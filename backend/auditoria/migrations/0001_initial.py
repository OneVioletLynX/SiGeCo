from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='RegistroAuditoria',
            fields=[
                ('id',             models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario_id',     models.IntegerField(blank=True, null=True)),
                ('usuario_nombre', models.CharField(blank=True, max_length=200)),
                ('accion',         models.CharField(choices=[('ALTA', 'Alta'), ('MODIFICACION', 'Modificación'), ('BAJA', 'Baja'), ('COBRO', 'Cobro')], max_length=20)),
                ('entidad',        models.CharField(max_length=50)),
                ('entidad_id',     models.IntegerField(blank=True, null=True)),
                ('descripcion',    models.CharField(max_length=500)),
                ('fecha',          models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
    ]
