"""Esquemas Pydantic para el módulo de Renovaciones y Servicios."""

from pydantic import BaseModel
from datetime import date
from typing import Optional


# ─── Servicio ──────────────────────────────────────────────────────────


class ServiceCreate(BaseModel):
    name: str
    description: str = ""


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ServiceResponse(BaseModel):
    id: str
    name: str
    description: str
    is_active: bool
    created_at: str
    updated_at: str


# ─── Renovación ────────────────────────────────────────────────────────


class RenewalCreate(BaseModel):
    supplier_id: str
    service_id: str
    contract_start_date: date
    contract_end_date: date
    renewal_notification_days: int = 30
    status: str = "active"
    notes: str = ""


class RenewalUpdate(BaseModel):
    supplier_id: Optional[str] = None
    service_id: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    renewal_notification_days: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class RenewalResponse(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    service_id: str
    service_name: str
    contract_start_date: date
    contract_end_date: date
    renewal_notification_days: int
    status: str
    notes: str
    is_active: bool
    created_at: str
    updated_at: str
