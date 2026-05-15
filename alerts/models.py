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


class AlertNotificationLog(models.Model):
    """
    Historial de envíos de alertas a través de los distintos canales.
    Registra cada intento de notificación con su resultado (éxito/falla)
    para llevar trazabilidad y facilitar la depuración.
    """

    STATUS_CHOICES = [
        ("success", "Éxito"),
        ("failed", "Falló"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Alerta a la que pertenece este registro de envío
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name="notification_logs",
        verbose_name="alerta",
    )
    # Canal por el que se intentó el envío (email, whatsapp)
    channel = models.CharField(
        max_length=20,
        verbose_name="canal",
    )
    # Estado del envío: éxito o falla
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name="estado",
    )
    # Destinatario al que se intentó enviar
    recipient = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="destinatario",
    )
    # Mensaje de error si el envío falló
    error_message = models.TextField(
        blank=True,
        default="",
        verbose_name="mensaje de error",
    )
    # Momento en que se realizó el envío
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="enviado el")

    class Meta:
        db_table = "alert_notification_logs"
        ordering = ["-sent_at"]
        verbose_name = "historial de envío"
        verbose_name_plural = "historial de envíos"

    def __str__(self):
        return f"{self.channel} - {self.status} - {self.alert.id}"
