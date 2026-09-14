from django.core.management.base import BaseCommand

from prestamos.services import actualizar_sistema


class Command(BaseCommand):
    help = 'Actualiza vencimientos, multas y avisos de prestamo.'

    def handle(self, *args, **options):
        actualizar_sistema()
        self.stdout.write(self.style.SUCCESS('Prestamos, multas y avisos actualizados.'))
