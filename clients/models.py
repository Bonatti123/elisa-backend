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


class Collaborator(models.Model):
    """Modelo que representa un colaborador de ELOMUX con datos personales, credenciales, rol, área, estado y CUPE"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Identificador único del colaborador
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="collaborator_profile"  # Vinculación al usuario de autenticación del sistema
    )
    phone = models.CharField(max_length=20, blank=True, default="")  # Teléfono de contacto del colaborador
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
    def __str__(self):
        """Devuelve el nombre completo del colaborador o su username si no tiene nombre"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
