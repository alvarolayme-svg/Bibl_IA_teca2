# prestamos/models.py
from django.db import models
from django.conf import settings
from catalogo.models import Libro

class Prestamo(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_limite = models.DateField()
    fecha_devolucion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')

    def __str__(self):
        return f"{self.usuario} - {self.libro} ({self.estado})"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('atendida', 'Atendida'),
        ('cancelada', 'Cancelada'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_reserva = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.usuario} reservo {self.libro}"

class Multa(models.Model):
    prestamo = models.OneToOneField(Prestamo, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    pagada = models.BooleanField(default=False)

    def __str__(self):
        return f"Multa {self.monto} - {'pagada' if self.pagada else 'pendiente'}"


class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('vencimiento', 'Vencimiento'),
        ('reserva', 'Reserva'),
        ('multa', 'Multa'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    prestamo = models.ForeignKey(Prestamo, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'prestamo', 'tipo'],
                name='notificacion_unica_por_prestamo',
            )
        ]

    def __str__(self):
        return self.mensaje
