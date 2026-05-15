"""Esquemas Pydantic para el módulo de Alertas."""

from pydantic import BaseModel
from typing import Optional


class AlertResponse(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    alert_type: str
    message: str
    is_read: bool
    created_at: str


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    unread_count: int
