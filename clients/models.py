import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("El username es obligatorio")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    permissions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, default="")
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def __str__(self):
        return self.username


# RF-35: Auditoría Transversal para Acciones Críticas
# Entidad común que registra toda operación sensible del sistema
# de forma inmutable y centralizada.
class GlobalAuditLog(models.Model):
    # Tipos de entidades auditables del sistema
    ENTITY_TYPES = [
        ("client", "Cliente"),
        ("user", "Usuario"),
        ("role", "Rol"),
        ("web_type", "Tipo de Web"),
        ("web_feature", "Característica"),
        ("change_request", "Solicitud de Cambio"),
        ("prospect", "Prospecto"),
        ("payment", "Pago"),
        ("system", "Sistema"),
    ]
    # Acciones críticas que se registran en la auditoría
    ACTION_TYPES = [
        ("create", "Creación"),
        ("update", "Actualización"),
        ("delete", "Eliminación"),
        ("login", "Inicio de sesión"),
        ("logout", "Cierre de sesión"),
        ("approve", "Aprobación"),
        ("reject", "Rechazo"),
        ("convert", "Conversión"),
        ("export", "Exportación"),
        ("other", "Otro"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Entidad afectada (ej: "client", "user", "payment")
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPES, db_index=True)
    # ID de la entidad afectada (opcional, ej: recién creada)
    entity_id = models.UUIDField(null=True, blank=True, db_index=True)
    # Acción ejecutada (ej: "create", "update", "delete")
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    # Descripción legible de lo ocurrido
    description = models.TextField(blank=True, default="")
    # Cambios específicos en formato JSON (valor_anterior / valor_nuevo)
    details = models.JSONField(default=dict, blank=True)
    # Dirección IP desde donde se ejecutó la acción
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    # User-Agent del navegador/cliente que realizó la acción
    user_agent = models.TextField(blank=True, default="")
    # Usuario que ejecutó la acción (nullable por si el usuario se elimina)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    # Marca temporal inmutable (se auto-asigna en la creación)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "global_audit_log"
        ordering = ["-created_at"]
        indexes = [
            # Índice compuesto para consultas por entidad
            models.Index(fields=["entity_type", "entity_id"]),
            # Índice compuesto para consultas por acción + fecha
            models.Index(fields=["action", "created_at"]),
        ]
        verbose_name = "Auditoría Global"
        verbose_name_plural = "Auditorías Globales"

    def __str__(self):
        return f"{self.get_action_display()} - {self.get_entity_type_display()} [{self.created_at}]"
