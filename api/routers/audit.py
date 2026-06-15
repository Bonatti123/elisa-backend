from fastapi import APIRouter, Depends, Query

from api.routers.auth import get_current_user
from api.schemas.audit import AuditLogEntry, AuditLogResponse
from clients.models import GlobalAuditLog, User

router = APIRouter()


# RF-35-T03: Endpoint para consultar la auditoria global.
# Filtros combinables: por modulo (entity_type), accion,
# usuario (performed_by) y rango de fechas (date_from/date_to).
# Acceso restringido a usuarios autenticados con token valido.
@router.get("/audit", response_model=AuditLogResponse)
def listar_auditoria(
    page: int = Query(1, ge=1, description="Numero de pagina"),
    page_size: int = Query(20, ge=1, le=100, description="Resultados por pagina"),
    entity_type: str | None = Query(None, description="Filtrar por modulo (client, user, etc.)"),
    action: str | None = Query(None, description="Filtrar por accion (create, update, login, etc.)"),
    performed_by: str | None = Query(None, description="Filtrar por ID de usuario"),
    date_from: str | None = Query(None, description="Fecha inicial (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="Fecha final (YYYY-MM-DD)"),
    user: User = Depends(get_current_user),
):
    # Construccion dinamica del queryset segun los filtros recibidos.
    # Solo se aplican los filtros que el frontend envia como parametro.
    qs = GlobalAuditLog.objects.all()

    if entity_type:
        qs = qs.filter(entity_type=entity_type)
    if action:
        qs = qs.filter(action=action)
    if performed_by:
        qs = qs.filter(performed_by_id=performed_by)
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    # Paginacion: se calcula el total antes del slice
    total = qs.count()
    offset = (page - 1) * page_size
    logs = qs.order_by("-created_at")[offset : offset + page_size]

    # Mapeo de modelos ORM a esquemas Pydantic para la respuesta JSON
    results = [
        AuditLogEntry(
            id=str(log.id),
            entity_type=log.entity_type,
            entity_id=str(log.entity_id) if log.entity_id else None,
            action=log.action,
            description=log.description,
            details=log.details,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            performed_by=str(log.performed_by_id) if log.performed_by_id else None,
            created_at=log.created_at,
        )
        for log in logs
    ]

    return AuditLogResponse(total=total, page=page, page_size=page_size, results=results)
