"""
Señales que disparan el motor de detección cuando se guarda un
proveedor o una renovación, creando alertas en tiempo real.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from suppliers.models import Supplier, Renewal
from suppliers.services.detector import (
    _crear_alerta_proveedor,
    _crear_alerta_renovacion,
)
from datetime import date


@receiver(post_save, sender=Supplier)
def verificar_proveedor_al_guardar(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza un proveedor, usa el motor de detección
    para verificar si está próximo a vencer o ya vencido.
    """
    if not instance.is_active or instance.status != "active":
        return

    today = date.today()
    dias_restantes = (instance.contract_end_date - today).days

    if instance.contract_end_date < today:
        # Caso: contrato ya vencido
        _crear_alerta_proveedor(instance, "expiration", dias_restantes, vencida=True)
    elif dias_restantes <= instance.renewal_notification_days:
        # Caso: contrato próximo a vencer
        _crear_alerta_proveedor(instance, "renewal", dias_restantes)


@receiver(post_save, sender=Renewal)
def verificar_renovacion_al_guardar(sender, instance, created, **kwargs):
    """
    Cuando se crea o actualiza una renovación, usa el motor de detección
    para verificar si está próxima a vencer o ya vencida.
    """
    if not instance.is_active or instance.status != "active":
        return

    today = date.today()
    dias_restantes = (instance.contract_end_date - today).days

    if instance.contract_end_date < today:
        # Caso: renovación ya vencida
        _crear_alerta_renovacion(
            instance, "expiration", dias_restantes, vencida=True
        )
    elif dias_restantes <= instance.renewal_notification_days:
        # Caso: renovación próxima a vencer
        _crear_alerta_renovacion(instance, "renewal", dias_restantes)
