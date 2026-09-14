from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='libro', name='anio_publicacion', field=models.PositiveIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='libro', name='creado_en', field=models.DateTimeField(auto_now_add=True, null=True)),
        migrations.AddField(model_name='libro', name='descripcion', field=models.TextField(blank=True)),
        migrations.AddField(model_name='libro', name='editorial', field=models.CharField(blank=True, max_length=120)),
        migrations.AddField(model_name='libro', name='imagen_url', field=models.URLField(blank=True)),
        migrations.AddField(model_name='libro', name='isbn', field=models.CharField(blank=True, max_length=20, null=True, unique=True)),
        migrations.AddField(model_name='libro', name='ubicacion', field=models.CharField(blank=True, max_length=80)),
    ]
