from django.apps import AppConfig


class AlertsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "alerts"
    verbose_name = "Alertas"

    def ready(self):
        import alerts.signals  # noqa: F401 - Conecta señales al iniciar
