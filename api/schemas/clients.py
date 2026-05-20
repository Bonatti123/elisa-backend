from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from pydantic.functional_validators import BeforeValidator


def coerce_uuid(v: object) -> str:
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern=r"^(RUC|DNI|CE|Pasaporte)$")
    document_number: str = Field(..., min_length=6, max_length=20)
    email: EmailStr
    phone: str = Field(..., max_length=50)
    web_type_id: str | None = None
    feature_ids: list[str] = Field(default=[])
    plan: str = Field(default="alquiler", pattern=r"^(alquiler|venta)$")
    initial_payment: Decimal | None = Field(default=None, gt=0)
    domain_price: Decimal | None = Field(default=None, ge=0)
    payment_frequency: str = Field(default="mensual", pattern=r"^(mensual|anual)$")
    registration_date: date | None = None
    notes: str = Field(default="", max_length=2000)


class ClientResponse(BaseModel):
    id: IdField
    cupe: str
    name: str
    document_type: str
    document_number: str
    email: str
    phone: str
    web_type: str | None = None
    features: list[dict] = []
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
    created_by: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ClientListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[ClientResponse]
