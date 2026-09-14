# catalogo/models.py
from django.db import models

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    categoria = models.CharField(max_length=100)
    editorial = models.CharField(max_length=120, blank=True)
    anio_publicacion = models.PositiveIntegerField(null=True, blank=True)
    ubicacion = models.CharField(max_length=80, blank=True)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=1)
    creado_en = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.titulo

    @property
    def disponible(self):
        return self.stock > 0
