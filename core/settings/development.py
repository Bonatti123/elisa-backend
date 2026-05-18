from .base import *

SECRET_KEY = os.getenv("SECRET_KEY", "mi-clave-local-elisa-2026")
DEBUG = True
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "alertas@elomux.com")
ALERT_EMAIL_RECIPIENTS = [
    r.strip()
    for r in os.getenv("ALERT_EMAIL_RECIPIENTS", "admin@elomux.com,gerencia@elomux.com").split(",")
    if r.strip()
]
ALERT_WHATSAPP_NUMBER = os.getenv("ALERT_WHATSAPP_NUMBER", "")
