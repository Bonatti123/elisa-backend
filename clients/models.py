import uuid
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """Manager personalizado para crear usuarios y superusuarios."""

    def create_user(self, username, password=None, **extra_fields):
        """Crea un usuario normal con username y contraseña."""
        if not username:
            raise ValueError("El username es obligatorio")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        """Crea un superusuario con permisos de staff y superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, password, **extra_fields)


class Role(models.Model):
    """Modelo que representa un rol dentro del sistema de permisos.
    Cada rol tiene un nombre único y un conjunto de permisos en JSON.
    """
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
    """Modelo personalizado de usuario que usa username como identificador principal.
    Reemplaza el User predeterminado de Django para integrarse con FastAPI.
    """
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


class Client(models.Model):
    """Modelo que representa un cliente del sistema.
    Almacena información de contacto, tipo de cliente y frecuencia de pago.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    client_type = models.CharField(max_length=50, blank=True, null=True, default="")
    payment_frequency = models.CharField(max_length=50, blank=True, null=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """Modelo que representa una campaña de marketing.
    Define el periodo de vigencia (start_date / end_date) y el presupuesto
    disponible. Las promociones pueden asociarse a una campaña.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaigns"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Promotion(models.Model):
    """Modelo que representa una promoción o descuento aplicable a clientes.
    Puede ser de tipo porcentaje o monto fijo, con condiciones como monto
    mínimo/máximo, tipo de cliente, tipo de web y frecuencia de pago.
    Opcionalmente se asocia a una Campaign para campañas de marketing.
    """
    APPLIES_TO_CHOICES = [
        ("quote", "Cotización"),
        ("service", "Servicio"),
        ("client", "Cliente"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    benefit_description = models.TextField(blank=True, default="")
    discount_type = models.CharField(max_length=20)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    applies_to = models.CharField(
        max_length=20, choices=APPLIES_TO_CHOICES, default="quote"
    )
    min_purchase_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    max_purchase_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    client_type = models.CharField(max_length=50, blank=True, null=True, default="")
    web_type_id = models.CharField(max_length=50, blank=True, null=True, default="")
    payment_frequency = models.CharField(max_length=50, blank=True, null=True, default="")
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promotions",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "promotions"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Intercepta el guardado para validar que las fechas de la promoción
        estén dentro del rango de la campaña asociada (si existe).
        Lanza ValidationError si valid_from es anterior a campaign.start_date
        o si valid_to es posterior a campaign.end_date.
        """
        if self.campaign_id is not None:
            try:
                campaign = Campaign.objects.get(id=self.campaign_id)
            except Campaign.DoesNotExist:
                raise ValidationError("La campaña asociada no existe")

            if self.valid_from is not None and self.valid_from.date() < campaign.start_date:
                raise ValidationError(
                    f"valid_from ({self.valid_from.date()}) no puede ser anterior "
                    f"a campaign.start_date ({campaign.start_date})"
                )
            if self.valid_to is not None and self.valid_to.date() > campaign.end_date:
                raise ValidationError(
                    f"valid_to ({self.valid_to.date()}) no puede ser posterior "
                    f"a campaign.end_date ({campaign.end_date})"
                )
        super().save(*args, **kwargs)
