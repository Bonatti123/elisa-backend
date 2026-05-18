from .base import *

SECRET_KEY = "test-secret-key-elomux-2026"
DEBUG = False

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_HOURS = 1

CORS_ALLOW_ALL_ORIGINS = False

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ═══════════════════════════════════════════════════════════════════════════════
#   ADVERTENCIA — MD5PasswordHasher
#   El uso de MD5PasswordHasher acelera los tests porque evita el costoso
#   hashing de bcrypt/argon2.  Sin embargo, MD5 NO es seguro para producción.
#   Cualquier atacante con acceso al hash de la contraseña podría revertirlo
#   en segundos.
#
#   →  NUNCA  uses MD5PasswordHasher en producción.
#   →  Si ves que alguien lo agrega en development.py o production.py,
#      detenelo y referí esta advertencia.
# ═══════════════════════════════════════════════════════════════════════════════
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

DEFAULT_FROM_EMAIL = "test@elomux.com"
ALERT_EMAIL_RECIPIENTS = []
ALERT_WHATSAPP_NUMBER = ""
