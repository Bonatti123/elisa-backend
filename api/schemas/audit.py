from datetime import datetime
from pydantic import BaseModel


# RF-35-T03: Esquemas de respuesta para la consulta de auditoria global
# AuditLogEntry: representa un registro individual de auditoria
# AuditLogResponse: envoltura paginada para el frontend
class AuditLogEntry(BaseModel):
    id: str
    entity_type: str
    entity_id: str | None = None
    action: str
    description: str
    details: dict
    ip_address: str | None = None
    user_agent: str | None = None
    performed_by: str | None = None
    created_at: datetime


class AuditLogResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[AuditLogEntry]
