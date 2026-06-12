import uuid
from typing import Any
from datetime import datetime, timezone
from clients.models import GlobalAuditLog, User


# RF-35: Servicio centralizado de auditoria.
# Todos los modulos llaman a esta funcion para registrar
# acciones criticas del sistema de forma consistente.
def registrar_auditoria(
    *,
    entity_type: str,
    action: str,
    description: str = "",
    details: dict[str, Any] | None = None,
    entity_id: str | uuid.UUID | None = None,
    performed_by: User | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> GlobalAuditLog:
    # Crea el registro de auditoria con los datos de la accion.
    # entity_type: tipo de entidad afectada (client, user, etc.)
    # action: accion ejecutada (create, update, login, etc.)
    # details: JSON con valores anteriores/nuevos si aplica
    return GlobalAuditLog.objects.create(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        description=description,
        details=details or {},
        performed_by=performed_by,
        ip_address=ip_address,
        user_agent=user_agent,
    )
