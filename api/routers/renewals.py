"""Router de FastAPI para Servicios y Renovaciones de proveedores."""

from fastapi import APIRouter, Depends, HTTPException, status
from django.core.exceptions import ValidationError

from api.schemas.renewals import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
    RenewalCreate,
    RenewalUpdate,
    RenewalResponse,
)
from api.routers.auth import get_current_user
from clients.models import User
from suppliers.models import Service, Renewal, Supplier

router = APIRouter()


# ─── Servicios ─────────────────────────────────────────────────────────


def _serialize_service(service: Service) -> ServiceResponse:
    """Convierte un modelo Service a su schema de respuesta."""
    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        description=service.description,
        is_active=service.is_active,
        created_at=service.created_at.isoformat(),
        updated_at=service.updated_at.isoformat(),
    )


@router.get("/services", response_model=list[ServiceResponse])
def list_services(user: User = Depends(get_current_user)):
    """Obtiene el catálogo de servicios activos."""
    services = Service.objects.filter(is_active=True)
    return [_serialize_service(s) for s in services]


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceCreate, user: User = Depends(get_current_user)):
    """Crea un nuevo servicio en el catálogo."""
    try:
        service = Service.objects.create(**body.model_dump())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _serialize_service(service)


@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(service_id: str, user: User = Depends(get_current_user)):
    """Obtiene un servicio por su ID."""
    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )
    return _serialize_service(service)


# ─── Renovaciones ──────────────────────────────────────────────────────


def _serialize_renewal(renewal: Renewal) -> RenewalResponse:
    """Convierte un modelo Renewal a su schema de respuesta."""
    return RenewalResponse(
        id=str(renewal.id),
        supplier_id=str(renewal.supplier.id),
        supplier_name=renewal.supplier.business_name,
        service_id=str(renewal.service.id),
        service_name=renewal.service.name,
        contract_start_date=renewal.contract_start_date,
        contract_end_date=renewal.contract_end_date,
        renewal_notification_days=renewal.renewal_notification_days,
        status=renewal.status,
        notes=renewal.notes,
        is_active=renewal.is_active,
        created_at=renewal.created_at.isoformat(),
        updated_at=renewal.updated_at.isoformat(),
    )


@router.get("/", response_model=list[RenewalResponse])
def list_renewals(user: User = Depends(get_current_user)):
    """Obtiene todas las renovaciones activas."""
    renewals = Renewal.objects.filter(
        is_active=True,
    ).select_related("supplier", "service")
    return [_serialize_renewal(r) for r in renewals]


@router.get("/{renewal_id}", response_model=RenewalResponse)
def get_renewal(renewal_id: str, user: User = Depends(get_current_user)):
    """Obtiene una renovación por su ID."""
    try:
        renewal = Renewal.objects.select_related("supplier", "service").get(
            id=renewal_id, is_active=True
        )
    except Renewal.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renovación no encontrada",
        )
    return _serialize_renewal(renewal)


@router.post("/", response_model=RenewalResponse, status_code=status.HTTP_201_CREATED)
def create_renewal(body: RenewalCreate, user: User = Depends(get_current_user)):
    """Crea un nuevo registro de renovación ligado a proveedor y servicio."""
    try:
        supplier = Supplier.objects.get(id=body.supplier_id, is_active=True)
    except Supplier.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    try:
        service = Service.objects.get(id=body.service_id, is_active=True)
    except Service.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servicio no encontrado",
        )

    try:
        renewal = Renewal.objects.create(
            supplier=supplier,
            service=service,
            contract_start_date=body.contract_start_date,
            contract_end_date=body.contract_end_date,
            renewal_notification_days=body.renewal_notification_days,
            status=body.status,
            notes=body.notes,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _serialize_renewal(renewal)


@router.put("/{renewal_id}", response_model=RenewalResponse)
def update_renewal(
    renewal_id: str,
    body: RenewalUpdate,
    user: User = Depends(get_current_user),
):
    """Actualiza los datos de una renovación existente."""
    try:
        renewal = Renewal.objects.select_related("supplier", "service").get(
            id=renewal_id, is_active=True
        )
    except Renewal.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renovación no encontrada",
        )

    update_data = body.model_dump(exclude_unset=True)

    if "supplier_id" in update_data:
        try:
            supplier = Supplier.objects.get(
                id=update_data.pop("supplier_id"), is_active=True
            )
            renewal.supplier = supplier
        except Supplier.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proveedor no encontrado",
            )

    if "service_id" in update_data:
        try:
            service = Service.objects.get(
                id=update_data.pop("service_id"), is_active=True
            )
            renewal.service = service
        except Service.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado",
            )

    for field, value in update_data.items():
        setattr(renewal, field, value)

    try:
        renewal.full_clean()
        renewal.save()
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _serialize_renewal(renewal)


@router.delete("/{renewal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_renewal(renewal_id: str, user: User = Depends(get_current_user)):
    """Elimina (desactiva) una renovación de forma lógica."""
    try:
        renewal = Renewal.objects.get(id=renewal_id, is_active=True)
    except Renewal.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Renovación no encontrada",
        )
    renewal.is_active = False
    renewal.save()
