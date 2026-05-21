from django.apps import AppConfig


class AuditConfig(AppConfig):
    # Configuración de la aplicación de auditoría
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"
