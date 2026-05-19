from datetime import date, datetime
from decimal import Decimal
from typing import Any

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator
from typing import Annotated


def coerce_uuid(v: object) -> str:
    return str(v) if isinstance(v, UUID) else v


IdField = Annotated[str, BeforeValidator(coerce_uuid)]


class PromotionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    benefit_description: str = Field(default="", max_length=1000)
    discount_type: str = Field(..., pattern=r"^(percentage|fixed)$")
    discount_value: Decimal = Field(..., gt=0)
    max_discount_amount: Decimal | None = Field(default=None, gt=0)
    applies_to: str = Field(default="quote", pattern=r"^(quote|service|client)$")
    min_purchase_amount: Decimal | None = Field(default=None, ge=0)
    max_purchase_amount: Decimal | None = Field(default=None, gt=0)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    client_type: str | None = Field(default=None, max_length=50)
    web_type_id: str | None = Field(default=None, max_length=50)
    payment_frequency: str | None = Field(default=None, max_length=50)
    campaign_id: str | None = None
    is_active: bool = True


class PromotionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    benefit_description: str | None = Field(default=None, max_length=1000)
    discount_type: str | None = Field(default=None, pattern=r"^(percentage|fixed)$")
    discount_value: Decimal | None = Field(default=None, gt=0)
    max_discount_amount: Decimal | None = Field(default=None, gt=0)
    applies_to: str | None = Field(default=None, pattern=r"^(quote|service|client)$")
    min_purchase_amount: Decimal | None = Field(default=None, ge=0)
    max_purchase_amount: Decimal | None = Field(default=None, gt=0)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    client_type: str | None = Field(default=None, max_length=50)
    web_type_id: str | None = Field(default=None, max_length=50)
    payment_frequency: str | None = Field(default=None, max_length=50)
    campaign_id: str | None = None
    is_active: bool | None = None


class PromotionResponse(BaseModel):
    id: IdField
    name: str
    description: str
    benefit_description: str
    discount_type: str
    discount_value: Decimal
    max_discount_amount: Decimal | None = None
    applies_to: str
    min_purchase_amount: Decimal | None = None
    max_purchase_amount: Decimal | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    client_type: str | None = None
    web_type_id: str | None = None
    payment_frequency: str | None = None
    campaign_id: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=1000)
    start_date: date
    end_date: date
    budget: Decimal = Field(..., gt=0)
    is_active: bool = True


class CampaignResponse(BaseModel):
    id: IdField
    name: str
    description: str
    start_date: date
    end_date: date
    budget: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class EvaluateRequest(BaseModel):
    client_id: str
    amount: Decimal = Field(..., gt=0)
    context_type: str = Field(default="quote", pattern=r"^(quote|service|client)$")
    web_type_id: str | None = None
    service_product_id: str | None = None


class EvaluateResponse(BaseModel):
    applicable_promotions: list[dict[str, Any]]
    best_promotion: dict[str, Any] | None = None
    original_amount: str
