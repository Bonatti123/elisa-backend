"""Esquemas Pydantic para el módulo de clientes.
Define las estructuras de datos para entrada y salida de la API.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import BeforeValidator


def coerce_uuid(v: object) -> str:
    """Convierte UUID a string para serialización."""
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


class ClientCreate(BaseModel):
    """Esquema para la creación de un nuevo cliente."""
    name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern=r"^(RUC|DNI|CE|Pasaporte)$")
    document_number: str = Field(..., min_length=6, max_length=20)
    email: EmailStr
    phone: str = Field(..., max_length=50)
    web_type_id: str | None = None  # ID del tipo de web contratado
    feature_ids: list[str] = Field(default=[])  # IDs de funcionalidades extra
    plan: str = Field(default="alquiler", pattern=r"^(alquiler|venta)$")
    initial_payment: Decimal | None = Field(default=None, gt=0)
    domain_price: Decimal | None = Field(default=None, ge=0)
    payment_frequency: str = Field(default="mensual", pattern=r"^(mensual|anual)$")
    registration_date: date | None = None
    notes: str = Field(default="", max_length=2000)


class ClientUpdate(BaseModel):
    """Esquema para la actualización de un cliente existente.
    Todos los campos son opcionales (actualización parcial).
    """
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    web_type_id: str | None = None
    feature_ids: list[str] | None = None
    plan: str | None = Field(default=None, pattern=r"^(alquiler|venta)$")
    status: str | None = Field(default=None, pattern=r"^(activo|inactivo|en_desarrollo)$")
    initial_payment: Decimal | None = Field(default=None, gt=0)
    domain_price: Decimal | None = Field(default=None, ge=0)
    payment_frequency: str | None = Field(default=None, pattern=r"^(mensual|anual)$")
    registration_date: date | None = None
    delivery_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class ClientResponse(BaseModel):
    """Esquema de respuesta con todos los datos del cliente."""
    id: IdField
    cupe: str  # Código único de cliente
    name: str
    document_type: str
    document_number: str
    email: str
    phone: str
    web_type: str | None = None  # Nombre del tipo de web
    features: list[dict] = []  # Lista de funcionalidades {id, name, extra_price}
    plan: str
    status: str
    base_price: Decimal
    extra_price: Decimal
    total_price: Decimal
    initial_payment: Decimal | None = None
    domain_price: Decimal | None = None
    payment_frequency: str
    registration_date: date | None = None
    delivery_date: date | None = None
    next_payment_date: date | None = None
    notes: str
    created_by: str | None = None  # Nombre de usuario que creó el registro
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseModel):
    """Esquema de respuesta paginada para listado de clientes."""
    total: int  # Total de registros que coinciden con los filtros
    page: int  # Página actual
    page_size: int  # Registros por página
    results: list[ClientResponse]  # Lista de clientes en esta página


class ChangeRequestCreate(BaseModel):
    """Esquema para solicitar un cambio sensible en un cliente."""
    campo: str = Field(..., max_length=100)
    valor_nuevo: Any
    motivo: str = Field(..., min_length=10, max_length=1000)


class ChangeRequestResponse(BaseModel):
    """Esquema de respuesta de una solicitud de cambio."""
    id: IdField
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
    """Esquema para aprobar o rechazar una solicitud de cambio."""
    estado: str = Field(..., pattern=r"^(aprobado|rechazado)$")
    motivo_rechazo: str | None = Field(default=None, max_length=500)
