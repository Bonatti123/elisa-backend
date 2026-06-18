from fastapi import APIRouter, Depends, HTTPException, status

from api.routers.auth import get_current_user
from api.schemas.web_types import WebTypeCreate, WebTypeUpdate, WebTypeResponse
from clients.models import WebType, User

router = APIRouter()


@router.get("/", response_model=list[WebTypeResponse])
def list_web_types(is_active: bool | None = None, user: User = Depends(get_current_user)):
    """Lista todos los tipos de web, con filtro opcional por is_active."""
    qs = WebType.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs.order_by("name")


@router.post("/", response_model=WebTypeResponse, status_code=status.HTTP_201_CREATED)
def create_web_type(body: WebTypeCreate, user: User = Depends(get_current_user)):
    """Crea un nuevo tipo de web. Solo personal autorizado (staff)."""
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
    if WebType.objects.filter(name__iexact=body.name).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El tipo de web ya existe")
    wt = WebType.objects.create(**body.model_dump())
    return wt


@router.put("/{web_type_id}", response_model=WebTypeResponse)
def update_web_type(web_type_id: str, body: WebTypeUpdate, user: User = Depends(get_current_user)):
    """Actualiza un tipo de web existente por su ID. Solo personal autorizado (staff)."""
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
    try:
        wt = WebType.objects.get(id=web_type_id)
    except WebType.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de web no encontrado")
    for attr, value in body.model_dump(exclude_unset=True).items():
        setattr(wt, attr, value)
    wt.save()
    return wt
