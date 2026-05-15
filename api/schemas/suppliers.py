"""Esquemas Pydantic para el módulo de Proveedores."""

from pydantic import BaseModel
from datetime import date
from typing import Optional


class SupplierCreate(BaseModel):
    business_name: str
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    service_description: str = ""
    contract_start_date: date
    contract_end_date: date
    renewal_notification_days: int = 30
    status: str = "active"


class SupplierUpdate(BaseModel):
    business_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    service_description: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    renewal_notification_days: Optional[int] = None
    status: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    business_name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    service_description: str
    contract_start_date: date
    contract_end_date: date
    renewal_notification_days: int
    status: str
    is_active: bool
    created_at: str
    updated_at: str
