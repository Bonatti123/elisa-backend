"""
Comando de gestión para detectar proveedores y renovaciones próximas
a vencer y crear alertas automáticamente.

Ejecutar: python manage.py check_renewals
Programar en cron diario para mantener las alertas actualizadas.
"""

from datetime import date
from django.core.management.base import BaseCommand
from suppliers.models import Supplier, Renewal
from alerts.models import Alert


class Command(BaseCommand):
    help = "Detecta renovaciones próximas a vencer y crea alertas"

    def handle(self, *args, **options):
        today = date.today()
        created_count = 0

        # ─── 1. Revisa proveedores con contrato próximo a vencer ──────
        suppliers = Supplier.objects.filter(
            is_active=True,
            status="active",
            contract_end_date__gte=today,
        )
        for supplier in suppliers:
            days_until_expiry = (supplier.contract_end_date - today).days
            if days_until_expiry <= supplier.renewal_notification_days:
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
                            f"Faltan {days_until_expiry} días."
                        ),
                    )
                    created_count += 1

        # ─── 2. Revisa renovaciones ligadas a proveedor y servicio ────
        renewals = Renewal.objects.filter(
            is_active=True,
            status="active",
            contract_end_date__gte=today,
        ).select_related("supplier", "service")
        for renewal in renewals:
            days_until_expiry = (renewal.contract_end_date - today).days
            if days_until_expiry <= renewal.renewal_notification_days:
                existing = Alert.objects.filter(
                    renewal=renewal,
                    alert_type="renewal",
                    is_read=False,
                ).exists()
                if not existing:
                    Alert.objects.create(
                        supplier=renewal.supplier,
                        renewal=renewal,
                        service=renewal.service,
                        alert_type="renewal",
                        message=(
                            f"Renovación de {renewal.service.name} - "
                            f"{renewal.supplier.business_name} "
                            f"vence el {renewal.contract_end_date}. "
                            f"Faltan {days_until_expiry} días."
                        ),
                    )
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Se crearon {created_count} alertas de renovación"
            )
        )
