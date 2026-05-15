"""
Comando de gestión para detectar proveedores próximos a vencer
y crear alertas de renovación automáticamente.

Ejecutar: python manage.py check_renewals
Programar en cron diario para mantener las alertas actualizadas.
"""

from datetime import date
from django.core.management.base import BaseCommand
from suppliers.models import Supplier
from alerts.models import Alert


class Command(BaseCommand):
    help = "Detecta proveedores próximos a vencer y crea alertas de renovación"

    def handle(self, *args, **options):
        today = date.today()
        # Busca proveedores activos cuya fecha de fin sea hoy o futura
        suppliers = Supplier.objects.filter(
            is_active=True,
            status="active",
            contract_end_date__gte=today,
        )
        created_count = 0
        for supplier in suppliers:
            days_until_expiry = (supplier.contract_end_date - today).days
            # Si está dentro del rango de notificación, crear alerta
            if days_until_expiry <= supplier.renewal_notification_days:
                # Evita duplicar alertas no leídas para el mismo proveedor
                existing = Alert.objects.filter(
                    supplier=supplier,
                    alert_type="renewal",
                    is_read=False,
                ).exists()
                if not existing:
                    Alert.objects.create(
                        supplier=supplier,
                        alert_type="renewal",
                        message=(
                            f"El contrato con {supplier.business_name} "
                            f"vence el {supplier.contract_end_date}. "
                            f"Faltan {days_until_expiry} días para el vencimiento."
                        ),
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Se crearon {created_count} alertas de renovación de proveedores"
            )
        )
