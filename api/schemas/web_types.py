from decimal import Decimal
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


def coerce_uuid(v: object) -> str:
    """Convierte un objeto UUID a string para serialización."""
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


class WebTypeCreate(BaseModel):
    """Esquema para la creación de un nuevo tipo de web."""
    name: str = Field(..., min_length=1, max_length=255)
    base_price_rent: Decimal = Field(..., gt=0)  # Precio base para plan alquiler
    base_price_sale: Decimal = Field(..., gt=0)  # Precio base para plan venta
    is_active: bool = True


class WebTypeUpdate(BaseModel):
    """Esquema para la actualización de un tipo de web existente. Todos los campos son opcionales."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    base_price_rent: Decimal | None = Field(default=None, gt=0)
    base_price_sale: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class WebTypeResponse(BaseModel):
    """Esquema de respuesta con los datos de un tipo de web."""
    id: IdField
    name: str
    base_price_rent: Decimal
    base_price_sale: Decimal
    is_active: bool
