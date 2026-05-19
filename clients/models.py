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


class WebType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    base_price_rent = models.DecimalField(max_digits=10, decimal_places=2)
    base_price_sale = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class WebFeature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "web_features"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Client(models.Model):
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
    cupe = models.CharField(max_length=50, blank=True, unique=True)
    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=20, blank=True, default="")
    document_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    web_type = models.ForeignKey(
        WebType, on_delete=models.PROTECT, null=True, blank=True, related_name="clients"
    )
    features = models.ManyToManyField(WebFeature, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="alquiler")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="en_desarrollo")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    initial_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    domain_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_frequency = models.CharField(
        max_length=20, choices=PAYMENT_FREQ_CHOICES, default="mensual"
    )
    registration_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    next_payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="clients_created"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clients"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
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

        super().save(*args, **kwargs)

    def update_prices(self):
        extra = sum(f.extra_price for f in self.features.all())
        self.extra_price = extra
        self.total_price = self.base_price + extra
        self.save(update_fields=["extra_price", "total_price"])
