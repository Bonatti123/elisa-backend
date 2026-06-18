from decimal import Decimal
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator


def coerce_uuid(v: object) -> str:
    """Convierte un objeto UUID a string para serialización."""
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


class WebFeatureCreate(BaseModel):
    """Esquema para la creación de una nueva funcionalidad web."""
    name: str = Field(..., min_length=1, max_length=255)
    extra_price: Decimal = Field(..., gt=0)  # Precio extra que se suma al plan base
    is_active: bool = True


class WebFeatureUpdate(BaseModel):
    """Esquema para la actualización de una funcionalidad web existente. Todos los campos son opcionales."""
    name: str | None = Field(default=None, min_length=1, max_length=255)
    extra_price: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None


class WebFeatureResponse(BaseModel):
    """Esquema de respuesta con los datos de una funcionalidad web."""
    id: IdField
    name: str
    extra_price: Decimal
    is_active: bool
