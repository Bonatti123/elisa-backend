import uuid
from django.db import models
from django.core.exceptions import ValidationError
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
    """Modelo personalizado de usuario para el sistema ERP ELISA - ELOMUX"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único del usuario
    username = models.CharField(max_length=150, unique=True)  # Nombre de usuario para inicio de sesión
    email = models.EmailField(unique=True, null=True, blank=True, default=None)  # Correo electrónico único del colaborador en el sistema
    first_name = models.CharField(max_length=150, blank=True, default="")  # Nombre del colaborador
    last_name = models.CharField(max_length=150, blank=True, default="")  # Apellido del colaborador
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"  # Rol asignado al colaborador
    )
    is_active = models.BooleanField(default=True)  # Indica si el colaborador está activo en el sistema
    is_staff = models.BooleanField(default=False)  # Indica si el colaborador tiene acceso al panel de administración
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora de creación del registro
    updated_at = models.DateTimeField(auto_now=True)  # Fecha y hora de la última modificación del registro

    objects = UserManager()

    USERNAME_FIELD = "username"  # Campo usado para autenticación
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"  # Nombre de la tabla en la base de datos
        ordering = ["username"]  # Ordenamiento por nombre de usuario

    def clean(self):
        """Valida que el email sea único en el sistema"""
        if self.email and User.objects.filter(email=self.email).exclude(pk=self.pk).exists():  # Verificar si el email ya está registrado
            raise ValidationError({"email": "El correo electrónico ya está registrado en el sistema"})

    def __str__(self):
        return self.username


class Collaborator(models.Model):
    """Modelo que representa un colaborador de ELOMUX con datos personales, credenciales, rol, área, estado y CUPE"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único del colaborador
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="collaborator_profile"  # Vinculación al usuario de autenticación del sistema
    )
    phone = models.CharField(max_length=20, blank=True, default="")  # Teléfono de contacto del colaborador
    document_number = models.CharField(max_length=50, unique=True, null=True, blank=True, default=None)  # Número de documento único del colaborador (INE, RFC, etc.)
    area = models.CharField(max_length=150, blank=True, default="")  # Área o departamento al que pertenece el colaborador
    cupe = models.CharField(max_length=50, blank=True, default="")  # Identificador CUPE del colaborador en el sistema
    hire_date = models.DateField(null=True, blank=True)  # Fecha en que el colaborador fue contratado
    notes = models.TextField(blank=True, default="")  # Notas u observaciones adicionales sobre el colaborador
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora de creación del registro
    updated_at = models.DateTimeField(auto_now=True)  # Fecha y hora de la última modificación del registro

    class Meta:
        db_table = "collaborators"  # Nombre de la tabla en la base de datos
        ordering = ["user__first_name", "user__last_name"]  # Ordenamiento por nombre del colaborador
        verbose_name = "Colaborador"  # Nombre singular en el admin de Django
        verbose_name_plural = "Colaboradores"  # Nombre plural en el admin de Django

    def clean(self):
        """Valida que el document_number sea único antes de guardar"""
        if self.document_number and Collaborator.objects.filter(document_number=self.document_number).exclude(pk=self.pk).exists():
            raise ValidationError({"document_number": "El número de documento ya existe en el sistema"})

    def save(self, *args, **kwargs):
        """Genera automáticamente el CUPE con prefijo ELO si no tiene uno asignado"""
        if not self.cupe:  # Solo generar si el colaborador no tiene CUPE asignado
            ultimo = Collaborator.objects.order_by("-created_at").first()  # Obtener el último colaborador registrado
            if ultimo and ultimo.cupe and ultimo.cupe.startswith("ELO-"):  # Verificar si ya existe un CUPE previo con prefijo ELO
                numero = int(ultimo.cupe.replace("ELO-", "")) + 1  # Incrementar el número del último CUPE
            else:
                numero = 1  # Si no hay colaboradores previos, empezar desde 1
            self.cupe = f"ELO-{numero:05d}"  # Asignar CUPE con formato de 5 dígitos (ej: ELO-00001)
        super().save(*args, **kwargs)

    def __str__(self):
        """Devuelve el nombre completo del colaborador o su username si no tiene nombre"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
