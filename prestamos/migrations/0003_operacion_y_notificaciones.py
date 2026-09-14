import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('prestamos', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestamo',
            name='fecha_limite',
            field=models.DateField(default=django.utils.timezone.localdate),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reserva',
            name='estado',
            field=models.CharField(
                choices=[('pendiente', 'Pendiente'), ('atendida', 'Atendida'), ('cancelada', 'Cancelada')],
                default='pendiente',
                max_length=12,
            ),
        ),
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('vencimiento', 'Vencimiento'), ('reserva', 'Reserva'), ('multa', 'Multa')], max_length=15)),
                ('mensaje', models.CharField(max_length=255)),
                ('leida', models.BooleanField(default=False)),
                ('creada_en', models.DateTimeField(auto_now_add=True)),
                ('prestamo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='prestamos.prestamo')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-creada_en']},
        ),
        migrations.AddConstraint(
            model_name='notificacion',
            constraint=models.UniqueConstraint(fields=('usuario', 'prestamo', 'tipo'), name='notificacion_unica_por_prestamo'),
        ),
    ]
