# Generated for the Biblioteca SIS application.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='tipo_usuario',
            field=models.CharField(
                choices=[
                    ('estudiante', 'Estudiante'),
                    ('docente', 'Docente'),
                    ('administrador', 'Administrador'),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='limite_prestamos',
            field=models.PositiveIntegerField(default=2, editable=False),
        ),
    ]
