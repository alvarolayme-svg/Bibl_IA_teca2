from django.db import migrations, models


def actualizar_estados_reserva(apps, schema_editor):
    Reserva = apps.get_model('prestamos', 'Reserva')
    Reserva.objects.filter(estado='atendida').update(estado='autorizada')
    Reserva.objects.filter(estado='cancelada').update(estado='rechazada')


class Migration(migrations.Migration):

    dependencies = [
        ('prestamos', '0003_operacion_y_notificaciones'),
    ]

    operations = [
        migrations.RunPython(actualizar_estados_reserva, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='reserva',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('autorizada', 'Autorizada'),
                    ('rechazada', 'Rechazada'),
                ],
                default='pendiente',
                max_length=12,
            ),
        ),
    ]
