import uuid
from datetime import date, timedelta
from django.conf import settings  # Configuración del proyecto para variables de entorno
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manager personalizado para el modelo User."""

    def create_user(self, username, password=None, **extra_fields):
        """Crea un usuario normal con username y password."""
        if not username:
            raise ValueError("El username es obligatorio")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Crea un superusuario con is_staff=True e is_superuser=True."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Role(models.Model):
    """Modelo de roles del sistema para control de acceso y permisos."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default="")
    permissions = models.JSONField(default=dict, blank=True)  # Permisos en formato JSON
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario del sistema con autenticación por username."""
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


class WebType(models.Model):
    """Catálogo de tipos de web con precios base por plan (alquiler/venta)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    base_price_rent = models.DecimalField(max_digits=10, decimal_places=2)  # Precio base alquiler
    base_price_sale = models.DecimalField(max_digits=10, decimal_places=2)  # Precio base venta
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class WebFeature(models.Model):
    """Catálogo de funcionalidades extra para webs con precio adicional."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2)  # Precio extra de la funcionalidad
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_features"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """Bitácora de auditoría para registrar cambios críticos en el sistema."""
    ACCIONES = [
        ("creacion", "Creación"),
        ("actualizacion", "Actualización"),
        ("eliminacion", "Eliminación"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="auditoria"
    )
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modulo = models.CharField(max_length=50)  # Ej: clients, auth, suppliers
    registro_id = models.CharField(max_length=100, blank=True, default="")  # ID del registro afectado
    detalle = models.JSONField(default=dict, blank=True)  # Cambios en formato JSON
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.accion} - {self.modulo} - {self.created_at}"


class Client(models.Model):
    """Modelo principal de clientes del sistema CRM."""
    STATUS_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("en_desarrollo", "En desarrollo"),
    ]
    PLAN_CHOICES = [
        ("alquiler", "Alquiler"),
        ("venta", "Venta"),
    ]
    PAYMENT_FREQ_CHOICES = [
        ("mensual", "Mensual"),
        ("anual", "Anual"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cupe = models.CharField(max_length=50, blank=True, unique=True)  # Código único de cliente ELO-XXXXX
    name = models.CharField(max_length=255)  # Nombre o razón social
    document_type = models.CharField(max_length=20, blank=True, default="")  # RUC/DNI/CE/Pasaporte
    document_number = models.CharField(max_length=50, unique=True)  # Número de documento
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    web_type = models.ForeignKey(
        WebType, on_delete=models.PROTECT, null=True, blank=True, related_name="clients"
    )  # Tipo de web contratado
    features = models.ManyToManyField(WebFeature, blank=True)  # Funcionalidades extra
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="alquiler")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_desarrollo")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Precio base del plan
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Suma de precios extra
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Precio total (base + extra)
    initial_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Pago inicial
    domain_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio del dominio
    payment_frequency = models.CharField(
        max_length=20, choices=PAYMENT_FREQ_CHOICES, default="mensual"
    )  # Frecuencia de pago
    registration_date = models.DateField(null=True, blank=True)  # Fecha de registro
    delivery_date = models.DateField(null=True, blank=True)  # Fecha de entrega
    next_payment_date = models.DateField(null=True, blank=True)  # Próxima fecha de pago
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="clients_created"
    )
    is_active = models.BooleanField(default=True)  # Soft delete: False si se dio de baja
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Genera el CUPE, calcula precios y actualiza fechas según el tipo de web y plan."""
        if not self.cupe:
            ultimo = Client.objects.order_by("-created_at").first()
            if ultimo and ultimo.cupe and ultimo.cupe.startswith("ELO-"):
                numero = int(ultimo.cupe.replace("ELO-", "")) + 1
            else:
                numero = 1
            self.cupe = f"ELO-{numero:05d}"

        if self.web_type_id:
            if self.plan == "alquiler":
                self.base_price = self.web_type.base_price_rent
            else:
                self.base_price = self.web_type.base_price_sale
            self.total_price = self.base_price

        if self.delivery_date and self.status == "en_desarrollo":
            self.status = "activo"
            if self.payment_frequency == "mensual":
                # Próximo pago: fecha de entrega + días configurados para alquiler (PLAN_RENEWAL_DAYS_RENT)
                self.next_payment_date = self.delivery_date + timedelta(days=settings.PLAN_RENEWAL_DAYS_RENT)
            else:
                # Próximo pago: fecha de entrega + días configurados para venta (PLAN_RENEWAL_DAYS_SALE)
                self.next_payment_date = self.delivery_date + timedelta(days=settings.PLAN_RENEWAL_DAYS_SALE)

        super().save(*args, **kwargs)

    def update_prices(self):
        """Recalcula el precio extra (suma de funcionalidades) y el precio total."""
        extra = sum(f.extra_price for f in self.features.all())
        self.extra_price = extra
        self.total_price = self.base_price + extra
        self.save(update_fields=["extra_price", "total_price"])


class ChangeRequest(models.Model):
    """Solicitud de cambio sensible en un cliente que requiere aprobación."""
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="change_requests"
    )
    campo = models.CharField(max_length=100)  # Campo solicitado a cambiar
    valor_anterior = models.JSONField(default=dict, blank=True)  # Valor antes del cambio
    valor_nuevo = models.JSONField(default=dict, blank=True)  # Valor solicitado
    motivo = models.TextField(blank=True, default="")
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    solicitado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="change_requests_made"
    )
    revisado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="change_requests_reviewed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "change_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campo} - {self.estado}"
