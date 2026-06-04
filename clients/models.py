import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Gestor personalizado para el modelo User.
    Proporciona métodos para crear usuarios regulares y superusuarios
    dentro del sistema de autenticación de la plataforma ELOMUX.
    """

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
    """Modelo de roles del sistema para control de acceso y permisos.
    Cada rol tiene un nombre único, una descripción opcional y un conjunto
    de permisos almacenados en formato JSON. Controla la jerarquía y las
    capacidades de cada colaborador dentro de ELOMUX.
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
    """Modelo de usuario del sistema con autenticación por username.
    Representa a cada colaborador registrado en la plataforma ELOMUX.
    Se autentica mediante username y password, y está asociado a un rol
    que define sus permisos dentro del sistema.
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


class WebType(models.Model):
    """Catálogo de tipos de web con precios base por plan (alquiler/venta).
    Almacena los distintos tipos de sitios web que ELOMUX ofrece a sus
    clientes, cada uno con un precio base diferenciado para alquiler mensual
    y venta única.
    """

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
    """Catálogo de funcionalidades extra para webs con precio adicional.
    Cada funcionalidad (ej: carrito de compras, sistema de citas) tiene un
    precio extra que se suma al precio base del tipo de web contratado.
    """

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


class AuditLog(models.Model):
    """Bitácora de auditoría para registrar cambios críticos en el sistema.
    Cada vez que se crea, actualiza o elimina un registro importante, se
    guarda una entrada en esta bitácora con el usuario responsable, la
    acción realizada y los detalles del cambio en formato JSON.
    """

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
    modulo = models.CharField(max_length=50)
    registro_id = models.CharField(max_length=100, blank=True, default="")
    detalle = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.accion} - {self.modulo} - {self.created_at}"


# #BE001: Entidad Core de Gestión de Clientes de la plataforma ELOMUX
class Client(models.Model):
    """Modelo principal de clientes del sistema CRM de ELOMUX.
    Almacena toda la información comercial y de servicio de cada cliente,
    incluyendo su plan contratado, estado actual, tipo de web asignado,
    funcionalidades extra, precios y fechas clave del ciclo de vida.
    """

    # Enumeraciones nativas de Django (TextChoices) para evitar dependencias
    # circulares y garantizar la integridad de los datos a nivel de BD.
    class ClientPlan(models.TextChoices):
        """Planes comerciales disponibles: alquiler mensual o venta única."""

        RENTAL = "alquiler", _("Alquiler")
        SALE = "venta", _("Venta")

    class ClientStatus(models.TextChoices):
        """Estados del ciclo de vida del cliente dentro del sistema."""

        ACTIVE = "activo", _("Activo")
        INACTIVE = "inactivo", _("Inactivo")
        UNDER_DEVELOPMENT = "en_desarrollo", _("En desarrollo")

    class PaymentFrequency(models.TextChoices):
        """Frecuencias de pago configuradas para las renovaciones."""

        MONTHLY = "mensual", _("Mensual")
        ANNUAL = "anual", _("Anual")

    # Identificador único universal para evitar colisiones en distribuidos
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Código único de cliente en formato ELO-XXXXX (se genera automáticamente)
    cupe = models.CharField(max_length=50, blank=True, unique=True)
    # Nombre o razón social del cliente
    name = models.CharField(max_length=255)
    # Tipo de documento: RUC, DNI, CE o Pasaporte
    document_type = models.CharField(max_length=20, blank=True, default="")
    # Número de documento único por cliente
    document_number = models.CharField(max_length=50, unique=True)
    # Correo electrónico de contacto del cliente
    email = models.EmailField()
    # Número de teléfono de contacto
    phone = models.CharField(max_length=50)
    # Tipo de web contratado (relación con el catálogo de tipos de web)
    web_type = models.ForeignKey(
        WebType, on_delete=models.PROTECT, null=True, blank=True, related_name="clients"
    )
    # Funcionalidades extra contratadas (relación muchos a muchos)
    features = models.ManyToManyField(WebFeature, blank=True)
    # Plan contratado: alquiler o venta
    plan = models.CharField(
        max_length=20, choices=ClientPlan.choices, default=ClientPlan.RENTAL
    )
    # Estado actual del cliente dentro del sistema
    status = models.CharField(
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.UNDER_DEVELOPMENT,
    )
    # Precio base del plan según el tipo de web seleccionado
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Suma de precios de todas las funcionalidades extra contratadas
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Precio total mensual/único (base + extra)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Monto del pago inicial registrado al crear el cliente
    initial_payment = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    # Precio del dominio propio si el cliente contrató uno
    domain_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    # Frecuencia de pago para renovaciones: mensual o anual
    payment_frequency = models.CharField(
        max_length=20,
        choices=PaymentFrequency.choices,
        default=PaymentFrequency.MONTHLY,
    )
    # Fecha en que se registró al cliente por primera vez
    registration_date = models.DateField(null=True, blank=True)
    # Fecha en que se entregó la web al cliente (activa el cliente)
    delivery_date = models.DateField(null=True, blank=True)
    # Próxima fecha de pago calculada automáticamente
    next_payment_date = models.DateField(null=True, blank=True)
    # Observaciones y notas adicionales sobre el cliente
    notes = models.TextField(blank=True, default="")
    # Usuario que creó el registro del cliente
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients_created",
    )
    # Soft delete: False si el cliente fue dado de baja
    is_active = models.BooleanField(default=True)
    # Fecha y hora de creación del registro
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha y hora de la última modificación
    updated_at = models.DateTimeField(auto_now=True)

    # Metadatos de la tabla en base de datos
    class Meta:
        db_table = "elomux_clients"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Genera el CUPE automáticamente y calcula el precio base.
        Si el cliente no tiene CUPE, se genera uno secuencial con formato
        ELO-XXXXX. Si tiene tipo de web asignado, se calcula el precio
        base según el plan (alquiler o venta).
        """
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
        """Recalcula el precio extra y el precio total del cliente.
        Suma el precio de todas las funcionalidades extra asociadas al
        cliente y actualiza los campos correspondientes en la BD.
        """
        extra = sum(f.extra_price for f in self.features.all())
        self.extra_price = extra
        self.total_price = self.base_price + extra
        self.save(update_fields=["extra_price", "total_price"])


# #BE002: Modelo de Auditoría e Historial de Modificaciones del Cliente
class ClientHistory(models.Model):
    """Historial de auditoría para rastrear modificaciones en clientes.
    Almacuna instantáneas del estado anterior y posterior de cada mutación
    realizada sobre un cliente, permitiendo la trazabilidad completa de
    todos los cambios hechos por los colaboradores del sistema.
    """

    # Cliente al que pertenece este registro de auditoría
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="audit_history"
    )
    # Colaborador que realizó la modificación
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="client_history_changes",
    )
    # Instantánea del estado del cliente antes de la modificación
    previous_state = models.JSONField(
        help_text="Instantánea del estado anterior a la mutación."
    )
    # Instantánea del estado del cliente después de la modificación
    new_state = models.JSONField(
        help_text="Instantánea del estado posterior a la mutación."
    )
    # Fecha y hora en que se realizó el cambio
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Nombre de tabla estandarizado con prefijo del proyecto
        db_table = "elomux_clients_history"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"History {self.id} - {self.client.name}"


class ChangeRequest(models.Model):
    """Solicitud de cambio sensible en un cliente que requiere aprobación.
    Cuando un colaborador solicita modificar un campo crítico de un cliente,
    esta entidad registra la solicitud con los valores anterior y nuevo,
    quedando pendiente de aprobación por parte de Superadmin o Scrum Master.
    """

    # Estados posibles de una solicitud de cambio
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]

    # Identificador único de la solicitud
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Cliente al que se solicita el cambio
    cliente = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="change_requests"
    )
    # Nombre del campo que se desea modificar
    campo = models.CharField(max_length=100)
    # Valor que tenía el campo antes de la solicitud
    valor_anterior = models.JSONField(default=dict, blank=True)
    # Nuevo valor solicitado para el campo
    valor_nuevo = models.JSONField(default=dict, blank=True)
    # Motivo o justificación del cambio solicitado
    motivo = models.TextField(blank=True, default="")
    # Estado actual de la solicitud (pendiente/aprobado/rechazado)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    # Usuario que realizó la solicitud de cambio
    solicitado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_requests_made",
    )
    # Usuario que revisó y aprobó/rechazó la solicitud
    revisado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_requests_reviewed",
    )
    # Fecha y hora de creación de la solicitud
    created_at = models.DateTimeField(auto_now_add=True)
    # Fecha y hora de la última actualización
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "change_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campo} - {self.estado}"
