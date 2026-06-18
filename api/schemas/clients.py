"""Esquemas Pydantic para el módulo de gestión de clientes.
Define los contratos JSON de entrada y salida para los endpoints REST
de clientes, garantizando la validación estricta de tipos en el perímetro
de la API de la plataforma ELOMUX.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import BeforeValidator


def coerce_uuid(v: object) -> str:
    """Convierte un objeto UUID a su representación en string."""
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


# #BE003: DTO de Validación Perimetral para Inserción de Clientes
class ClientBase(BaseModel):
    """Esquema base con los campos comunes de un cliente.
    Define la estructura fundamental que comparten los DTOs de creación,
    actualización y respuesta del módulo de clientes.
    """

    name: str = Field(
        ..., max_length=255, description="Nombre o razón social del cliente"
    )
    document_number: str = Field(
        ..., max_length=50, description="Número de documento único"
    )
    email: EmailStr
    plan: str = Field(
        default="alquiler", description="Plan contratado: alquiler o venta"
    )
    status: str = Field(
        default="en_desarrollo", description="Estado actual del cliente"
    )
    payment_frequency: str = Field(
        default="mensual", description="Frecuencia de pago: mensual o anual"
    )


class ClientCreate(ClientBase):
    """DTO para la creación de un nuevo cliente en el sistema.
    Hereda todos los campos de ClientBase y agrega los campos específicos
    requeridos al momento del registro inicial del cliente en ELOMUX.
    """

    document_type: str = Field(..., pattern=r"^(RUC|DNI|CE|Pasaporte)$")
    phone: str = Field(..., max_length=50)
    web_type_id: str | None = None
    feature_ids: list[str] = Field(default=[])
    initial_payment: Decimal | None = Field(default=None, gt=0)
    domain_price: Decimal | None = Field(default=None, ge=0)
    registration_date: date | None = None
    notes: str = Field(default="", max_length=2000)


class ClientUpdate(BaseModel):
    """DTO para la actualización parcial de un cliente existente.
    Todos los campos son opcionales para permitir actualizaciones parciales
    (PATCH) sin necesidad de enviar el objeto completo.
    """

    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    web_type_id: str | None = None
    feature_ids: list[str] | None = None
    plan: str | None = Field(default=None, pattern=r"^(alquiler|venta)$")
    status: str | None = Field(
        default=None, pattern=r"^(activo|inactivo|en_desarrollo)$"
    )
    initial_payment: Decimal | None = Field(default=None, gt=0)
    domain_price: Decimal | None = Field(default=None, ge=0)
    payment_frequency: str | None = Field(default=None, pattern=r"^(mensual|anual)$")
    registration_date: date | None = None
    delivery_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


# #BE004: DTO de Respuesta Homologada del Ciclo de Vida del Cliente
class ClientResponse(ClientBase):
    """DTO de respuesta con todos los datos del cliente.
    Se utiliza en los endpoints de detalle y listado para devolver la
    información completa del cliente de forma homologada.
    """

    id: str
    cupe: str
    document_type: str
    phone: str
    web_type: str | None = None
    features: list[dict] = []
    base_price: Decimal = Field(default=0, description="Precio base del plan")
    extra_price: Decimal = Field(default=0, description="Suma de funcionalidades extra")
    total_price: Decimal = Field(default=0, description="Precio total (base + extra)")
    initial_payment: Decimal | None = None
    domain_price: Decimal | None = None
    registration_date: date | None = None
    delivery_date: date | None = None
    next_payment_date: date | None = None
    notes: str = ""
    created_by: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientListResponse(BaseModel):
    """DTO para la respuesta paginada del listado de clientes.
    Incluye metadatos de paginación además de la lista de resultados.
    """

    total: int
    page: int
    page_size: int
    results: list[ClientResponse]


class ChangeRequestCreate(BaseModel):
    """DTO para solicitar un cambio sensible en los datos de un cliente.
    El colaborador indica qué campo desea modificar, el nuevo valor y el
    motivo del cambio. Queda pendiente de aprobación por un superior.
    """

    campo: str = Field(..., max_length=100)
    valor_nuevo: Any
    motivo: str = Field(..., min_length=10, max_length=1000)


class ChangeRequestResponse(BaseModel):
    """DTO de respuesta para una solicitud de cambio sensible.
    Incluye la información completa de la solicitud, quién la hizo y
    quién la revisó, así como su estado actual.
    """

    id: str
    cliente_id: str
    campo: str
    valor_anterior: dict
    valor_nuevo: dict
    motivo: str
    estado: str
    solicitado_por: str | None = None
    revisado_por: str | None = None
    created_at: datetime
    updated_at: datetime


class ChangeRequestReview(BaseModel):
    """DTO para aprobar o rechazar una solicitud de cambio sensible.
    Solo los usuarios con permisos de staff pueden usar este esquema.
    """

    estado: str = Field(..., pattern=r"^(aprobado|rechazado)$")
    motivo_rechazo: str | None = Field(default=None, max_length=500)
