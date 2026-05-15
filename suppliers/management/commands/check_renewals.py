"""
Comando de gestión que utiliza el motor de detección para encontrar
renovaciones próximas y vencidas, y crear alertas automáticamente.

Ejecutar: python manage.py check_renewals
Programar en cron diario para mantener las alertas actualizadas.
"""

from django.core.management.base import BaseCommand
from suppliers.services.detector import detectar_todo


class Command(BaseCommand):
    help = "Detecta renovaciones próximas y vencidas usando el motor de detección"

    def handle(self, *args, **options):
        """
        Ejecuta el motor de detección completo y reporta
        cuántas alertas se crearon.
        """
        total = detectar_todo()

        if total > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Motor de detección: se crearon {total} alertas"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Motor de detección: no se detectaron novedades"
                )
            )
