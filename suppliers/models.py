import uuid
from django.db import models


class Supplier(models.Model):
    """Modelo que representa un proveedor externo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(
        max_length=255,
        verbose_name="razón social",
    )
    contact_name = models.CharField(
        max_length=150, blank=True, default="",
        verbose_name="nombre de contacto",
    )
    contact_email = models.EmailField(
        blank=True, default="",
        verbose_name="correo de contacto",
    )
    contact_phone = models.CharField(
        max_length=50, blank=True, default="",
        verbose_name="teléfono de contacto",
    )
    service_description = models.TextField(
        blank=True, default="",
        verbose_name="servicio que provee",
    )
    # Fechas del contrato para detectar renovaciones
    contract_start_date = models.DateField(verbose_name="inicio del contrato")
    contract_end_date = models.DateField(verbose_name="fin del contrato")
    # Días antes del vencimiento para generar la alerta
    renewal_notification_days = models.PositiveIntegerField(
        default=30,
        verbose_name="días antes para notificar",
    )
    status = models.CharField(
        max_length=20,
        choices=[("active", "Activo"), ("inactive", "Inactivo")],
        default="active",
        verbose_name="estado",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"
        ordering = ["business_name"]
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.business_name


class Service(models.Model):
    """Catálogo de servicios que los proveedores pueden ofrecer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="nombre del servicio",
    )
    description = models.TextField(
        blank=True, default="",
        verbose_name="descripción",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "services"
        ordering = ["name"]
        verbose_name = "servicio"
        verbose_name_plural = "servicios"

    def __str__(self):
        return self.name


class Renewal(models.Model):
    """
    Registro de renovación que vincula un proveedor con un servicio
    y sus fechas de contrato para detectar vencimientos próximos.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Proveedor al que pertenece esta renovación
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name="renewals",
        verbose_name="proveedor",
    )
    # Servicio contratado (ej. hosting, dominio, soporte)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="renewals",
        verbose_name="servicio",
    )
    contract_start_date = models.DateField(verbose_name="inicio del contrato")
    contract_end_date = models.DateField(verbose_name="fin del contrato")
    # Días antes del vencimiento para lanzar la alerta
    renewal_notification_days = models.PositiveIntegerField(
        default=30,
        verbose_name="días antes para notificar",
    )
    status = models.CharField(
        max_length=20,
        choices=[("active", "Activo"), ("inactive", "Inactivo")],
        default="active",
        verbose_name="estado",
    )
    notes = models.TextField(
        blank=True, default="",
        verbose_name="notas",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "renewals"
        ordering = ["contract_end_date"]
        verbose_name = "renovación"
        verbose_name_plural = "renovaciones"

    def __str__(self):
        return f"{self.supplier.business_name} - {self.service.name}"
