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
