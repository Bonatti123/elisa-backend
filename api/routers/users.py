from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.routers.auth import get_current_user
from api.schemas.users import CollaboratorResponse
from clients.models import User, Collaborator

router = APIRouter()

ROLES_PERMITIDOS = {"SA", "SM", "TL", "LI"}


@router.get("/users", response_model=list[CollaboratorResponse])
def list_collaborators(
    is_active: bool | None = None,
    current_user: User = Depends(get_current_user),
):
    """Lista todos los colaboradores del sistema. Developer no tiene acceso."""
    if not current_user.role or current_user.role.name not in ROLES_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a este recurso",
        )

    qs = Collaborator.objects.select_related("user__role").all()

    if is_active is not None:
        qs = qs.filter(user__is_active=is_active)

    return [
        CollaboratorResponse(
            id=c.id,
            cupe=c.cupe,
            first_name=c.user.first_name,
            last_name=c.user.last_name,
            role_name=c.user.role.name if c.user.role else None,
            city=c.city,
            is_active=c.user.is_active,
        )
        for c in qs
    ]
