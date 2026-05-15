"""
Señales para crear alertas automáticas cuando se guarda un proveedor
cuya fecha de fin está próxima a vencer.
"""

from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from suppliers.models import Supplier
from .models import Alert


@receiver(post_save, sender=Supplier)
def check_supplier_renewal_on_save(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un proveedor, verifica si está
    próximo a vencer y crea una alerta si corresponde.
    """
    # Solo procesa proveedores activos
    if not instance.is_active or instance.status != "active":
        return

    today = date.today()
    # Si la fecha ya pasó, no genera alerta
    if instance.contract_end_date < today:
        return

    days_until_expiry = (instance.contract_end_date - today).days

    # Si está dentro del rango de notificación, crea la alerta
    if days_until_expiry <= instance.renewal_notification_days:
        # Evita duplicar si ya existe una alerta sin leer
        existing = Alert.objects.filter(
            supplier=instance,
            alert_type="renewal",
            is_read=False,
        ).exists()
        if not existing:
            Alert.objects.create(
                supplier=instance,
                alert_type="renewal",
                message=(
                    f"El contrato con {instance.business_name} "
                    f"vence el {instance.contract_end_date}. "
                    f"Faltan {days_until_expiry} días para el vencimiento."
                ),
            )
