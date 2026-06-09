"""Esquemas Pydantic para el módulo de contabilidad (compras, ventas y resumen financiero).
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class PurchaseCreate(BaseModel):
    """Esquema para registrar una nueva compra."""
    provider_name: str = Field(..., min_length=1, max_length=255)
    document_type: str = Field(..., pattern=r"^(invoice|receipt|credit_note|debit_note)$")
    document_number: str = Field(default="", max_length=100)
    amount: Decimal = Field(..., gt=0)
    issue_date: date
    category: str = Field(default="", max_length=100)
    attachment: str = Field(default="", max_length=500)
    notes: str = Field(default="", max_length=1000)


class PurchaseUpdate(BaseModel):
    """Esquema para actualizar una compra existente. Todos los campos son opcionales."""
    provider_name: str | None = Field(default=None, min_length=1, max_length=255)
    document_type: str | None = Field(default=None, pattern=r"^(invoice|receipt|credit_note|debit_note)$")
    document_number: str | None = Field(default=None, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0)
    issue_date: date | None = None
    category: str | None = Field(default=None, max_length=100)
    attachment: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=1000)


class PurchaseResponse(BaseModel):
    """Esquema de respuesta con los datos completos de una compra."""
    id: str
    provider_name: str
    document_type: str
    document_number: str
    amount: Decimal
    issue_date: date
    category: str
    attachment: str
    notes: str
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class SaleCreate(BaseModel):
    """Esquema para registrar una nueva venta."""
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: str = Field(default="", max_length=254)
    document_type: str = Field(..., pattern=r"^(invoice|receipt|credit_note|debit_note)$")
    document_number: str = Field(default="", max_length=100)
    amount: Decimal = Field(..., gt=0)
    issue_date: date
    status: str = Field(default="pending", pattern=r"^(pending|paid|cancelled|partial)$")
    category: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=1000)


class SaleUpdate(BaseModel):
    """Esquema para actualizar una venta existente. Todos los campos son opcionales."""
    client_name: str | None = Field(default=None, min_length=1, max_length=255)
    client_email: str | None = Field(default=None, max_length=254)
    document_type: str | None = Field(default=None, pattern=r"^(invoice|receipt|credit_note|debit_note)$")
    document_number: str | None = Field(default=None, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0)
    issue_date: date | None = None
    status: str | None = Field(default=None, pattern=r"^(pending|paid|cancelled|partial)$")
    category: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class SaleResponse(BaseModel):
    """Esquema de respuesta con los datos completos de una venta."""
    id: str
    client_name: str
    client_email: str
    document_type: str
    document_number: str
    amount: Decimal
    issue_date: date
    status: str
    category: str
    notes: str
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class FinancialSummaryResponse(BaseModel):
    """Esquema de respuesta con el balance resumido de ingresos y egresos por período."""
    total_purchases: Decimal
    total_sales: Decimal
    balance: Decimal
    purchase_count: int
    sale_count: int
    period_start: date
    period_end: date
