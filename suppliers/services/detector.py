"""
Motor de detección de renovaciones próximas y vencidas.

Centraliza la lógica para detectar:
- Renovaciones próximas a vencer (dentro de la ventana de notificación)
- Renovaciones vencidas (fecha de fin ya pasó)

Este módulo es usado por:
- Comando de gestión check_renewals (ejecución programada)
- Señales post_save de Supplier y Renewal (tiempo real)
"""

from datetime import date
from suppliers.models import Supplier, Renewal
from alerts.models import Alert


# ─── Funciones auxiliares ─────────────────────────────────────────────


def _crear_alerta_proveedor(supplier, tipo_alerta, dias_restantes, vencida=False):
    """
    Crea una alerta para un proveedor si no existe una similar sin leer.
    Retorna True si se creó la alerta, False si ya existía.
    """
    if vencida:
        mensaje = (
            f"El contrato con {supplier.business_name} "
            f"venció el {supplier.contract_end_date}. "
            f"Han pasado {abs(dias_restantes)} días desde el vencimiento."
        )
    else:
        mensaje = (
            f"El contrato con {supplier.business_name} "
            f"vence el {supplier.contract_end_date}. "
            f"Faltan {dias_restantes} días para el vencimiento."
        )

    # Evita duplicar alertas no leídas del mismo tipo para el mismo proveedor
    existe = Alert.objects.filter(
        supplier=supplier,
        alert_type=tipo_alerta,
        is_read=False,
    ).exists()

    if not existe:
        Alert.objects.create(
            supplier=supplier,
            alert_type=tipo_alerta,
            message=mensaje,
        )
        return True
    return False


def _crear_alerta_renovacion(renewal, tipo_alerta, dias_restantes, vencida=False):
    """
    Crea una alerta para un registro de renovación si no existe una similar
    sin leer. Retorna True si se creó la alerta, False si ya existía.
    """
    if vencida:
        mensaje = (
            f"Renovación de {renewal.service.name} - "
            f"{renewal.supplier.business_name} "
            f"venció el {renewal.contract_end_date}. "
            f"Han pasado {abs(dias_restantes)} días desde el vencimiento."
        )
    else:
        mensaje = (
            f"Renovación de {renewal.service.name} - "
            f"{renewal.supplier.business_name} "
            f"vence el {renewal.contract_end_date}. "
            f"Faltan {dias_restantes} días."
        )

    # Evita duplicar alertas no leídas del mismo tipo para la misma renovación
    existe = Alert.objects.filter(
        renewal=renewal,
        alert_type=tipo_alerta,
        is_read=False,
    ).exists()

    if not existe:
        Alert.objects.create(
            supplier=renewal.supplier,
            renewal=renewal,
            service=renewal.service,
            alert_type=tipo_alerta,
            message=mensaje,
        )
        return True
    return False


# ─── Detección para Supplier ──────────────────────────────────────────


def detectar_proveedores_proximos(today=None):
    """
    Detecta proveedores activos cuya fecha de fin está dentro de la
    ventana de notificación y crea alertas de tipo 'renewal'.
    """
    if today is None:
        today = date.today()

    proveedores = Supplier.objects.filter(
        is_active=True,
        status="active",
        contract_end_date__gte=today,
    )

    creadas = 0
    for proveedor in proveedores:
        dias_restantes = (proveedor.contract_end_date - today).days
        if dias_restantes <= proveedor.renewal_notification_days:
            if _crear_alerta_proveedor(proveedor, "renewal", dias_restantes):
                creadas += 1

    return creadas


def detectar_proveedores_vencidos(today=None):
    """
    Detecta proveedores activos cuya fecha de fin ya pasó y crea
    alertas de tipo 'expiration'.
    """
    if today is None:
        today = date.today()

    proveedores = Supplier.objects.filter(
        is_active=True,
        status="active",
        contract_end_date__lt=today,
    )

    creadas = 0
    for proveedor in proveedores:
        dias_restantes = (proveedor.contract_end_date - today).days
        if not Alert.objects.filter(
            supplier=proveedor,
            alert_type="expiration",
            is_read=False,
        ).exists():
            if _crear_alerta_proveedor(proveedor, "expiration", dias_restantes, vencida=True):
                creadas += 1

    return creadas


# ─── Detección para Renewal ───────────────────────────────────────────


def detectar_renovaciones_proximas(today=None):
    """
    Detecta renovaciones activas cuya fecha de fin está dentro de la
    ventana de notificación y crea alertas de tipo 'renewal'.
    """
    if today is None:
        today = date.today()

    renovaciones = Renewal.objects.filter(
        is_active=True,
        status="active",
        contract_end_date__gte=today,
    ).select_related("supplier", "service")

    creadas = 0
    for renovacion in renovaciones:
        dias_restantes = (renovacion.contract_end_date - today).days
        if dias_restantes <= renovacion.renewal_notification_days:
            if _crear_alerta_renovacion(renovacion, "renewal", dias_restantes):
                creadas += 1

    return creadas


def detectar_renovaciones_vencidas(today=None):
    """
    Detecta renovaciones activas cuya fecha de fin ya pasó y crea
    alertas de tipo 'expiration'.
    """
    if today is None:
        today = date.today()

    renovaciones = Renewal.objects.filter(
        is_active=True,
        status="active",
        contract_end_date__lt=today,
    ).select_related("supplier", "service")

    creadas = 0
    for renovacion in renovaciones:
        dias_restantes = (renovacion.contract_end_date - today).days
        if not Alert.objects.filter(
            renewal=renovacion,
            alert_type="expiration",
            is_read=False,
        ).exists():
            if _crear_alerta_renovacion(
                renovacion, "expiration", dias_restantes, vencida=True
            ):
                creadas += 1

    return creadas


# ─── Ejecución completa ───────────────────────────────────────────────


def detectar_todo(today=None):
    """
    Ejecuta las cuatro detecciones (próximas y vencidas para proveedores
    y renovaciones) y retorna el total de alertas creadas.
    """
    if today is None:
        today = date.today()

    total = 0
    total += detectar_proveedores_proximos(today)
    total += detectar_proveedores_vencidos(today)
    total += detectar_renovaciones_proximas(today)
    total += detectar_renovaciones_vencidas(today)
    return total
