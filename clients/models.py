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


class Purchase(models.Model):
    """Modelo de compra: representa un comprobante de compra (boleta o factura)."""

    DOCUMENT_TYPE_CHOICES = [
        ("invoice", "Factura"),
        ("receipt", "Boleta"),
        ("credit_note", "Nota de crédito"),
        ("debit_note", "Nota de débito"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_name = models.CharField(max_length=255)  # Nombre del proveedor
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)  # Tipo de comprobante
    document_number = models.CharField(max_length=100, blank=True, default="")  # Número de comprobante
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Monto total
    issue_date = models.DateField()  # Fecha de emisión
    category = models.CharField(max_length=100, blank=True, default="")  # Categoría contable
    attachment = models.CharField(max_length=500, blank=True, default="")  # Ruta del archivo adjunto
    notes = models.TextField(blank=True, default="")  # Observaciones
    is_active = models.BooleanField(default=True)  # Soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchases"
        ordering = ["-issue_date", "-created_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} {self.document_number} - {self.provider_name}"


class Sale(models.Model):
    """Modelo de venta: representa un comprobante de venta (boleta o factura)."""

    DOCUMENT_TYPE_CHOICES = [
        ("invoice", "Factura"),
        ("receipt", "Boleta"),
        ("credit_note", "Nota de crédito"),
        ("debit_note", "Nota de débito"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("paid", "Pagado"),
        ("cancelled", "Anulado"),
        ("partial", "Pago parcial"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=255)  # Nombre del cliente
    client_email = models.EmailField(blank=True, default="")  # Correo del cliente
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)  # Tipo de comprobante
    document_number = models.CharField(max_length=100, blank=True, default="")  # Número de comprobante
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # Monto total
    issue_date = models.DateField()  # Fecha de emisión
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # Estado de pago
    category = models.CharField(max_length=100, blank=True, default="")  # Categoría contable
    notes = models.TextField(blank=True, default="")  # Observaciones
    is_active = models.BooleanField(default=True)  # Soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sales"
        ordering = ["-issue_date", "-created_at"]

    def __str__(self):
        return f"{self.get_document_type_display()} {self.document_number} - {self.client_name}"
