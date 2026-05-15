import uuid
from django.db import models


class Alert(models.Model):
    """Modelo que representa una alerta o notificación del sistema."""

    ALERT_TYPES = [
        ("renewal", "Renovación"),
        ("expiration", "Vencimiento"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Proveedor asociado a la alerta (ej. renovación de contrato)
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="proveedor",
    )
    # Registro de renovación específica que originó la alerta
    renewal = models.ForeignKey(
        "suppliers.Renewal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
        verbose_name="renovación",
    )
    # Servicio relacionado con la alerta
    service = models.ForeignKey(
        "suppliers.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
        verbose_name="servicio",
    )
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        verbose_name="tipo de alerta",
    )
    message = models.TextField(verbose_name="mensaje")
    is_read = models.BooleanField(default=False, verbose_name="leída")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alerts"
        ordering = ["-created_at"]
        verbose_name = "alerta"
        verbose_name_plural = "alertas"

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.supplier.business_name}"
