from django.contrib import admin

from .models import Prestamo, Reserva, Multa, Notificacion 
admin.site.register(Prestamo) 
admin.site.register(Reserva) 
admin.site.register(Multa)
admin.site.register(Notificacion)
# Register your models here.
