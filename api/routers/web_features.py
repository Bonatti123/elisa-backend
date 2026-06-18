from fastapi import APIRouter, Depends, HTTPException, status

from api.routers.auth import get_current_user
from api.schemas.web_features import WebFeatureCreate, WebFeatureUpdate, WebFeatureResponse
from clients.models import WebFeature, User

router = APIRouter()


@router.get("/", response_model=list[WebFeatureResponse])
def list_web_features(is_active: bool | None = None, user: User = Depends(get_current_user)):
    """Lista todas las funcionalidades web, con filtro opcional por is_active."""
    qs = WebFeature.objects.all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs.order_by("name")


@router.post("/", response_model=WebFeatureResponse, status_code=status.HTTP_201_CREATED)
def create_web_feature(body: WebFeatureCreate, user: User = Depends(get_current_user)):
    """Crea una nueva funcionalidad web. Solo personal autorizado (staff)."""
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
    if WebFeature.objects.filter(name__iexact=body.name).exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La funcionalidad ya existe")
    wf = WebFeature.objects.create(**body.model_dump())
    return wf


@router.put("/{feature_id}", response_model=WebFeatureResponse)
def update_web_feature(feature_id: str, body: WebFeatureUpdate, user: User = Depends(get_current_user)):
    """Actualiza una funcionalidad web existente por su ID. Solo personal autorizado (staff)."""
    if not user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
    try:
        wf = WebFeature.objects.get(id=feature_id)
    except WebFeature.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Funcionalidad no encontrada")
    for attr, value in body.model_dump(exclude_unset=True).items():
        setattr(wf, attr, value)
    wf.save()
    return wf
