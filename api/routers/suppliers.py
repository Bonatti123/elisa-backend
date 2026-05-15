"""Router de FastAPI para el módulo de Proveedores."""

from fastapi import APIRouter, Depends, HTTPException, status
from django.core.exceptions import ValidationError

from api.schemas.suppliers import SupplierCreate, SupplierUpdate, SupplierResponse
from api.routers.auth import get_current_user
from clients.models import User
from suppliers.models import Supplier

router = APIRouter()


def _serialize_supplier(supplier: Supplier) -> SupplierResponse:
    """Convierte un modelo Supplier a su schema de respuesta."""
    return SupplierResponse(
        id=str(supplier.id),
        business_name=supplier.business_name,
        contact_name=supplier.contact_name,
        contact_email=supplier.contact_email,
        contact_phone=supplier.contact_phone,
        service_description=supplier.service_description,
        contract_start_date=supplier.contract_start_date,
        contract_end_date=supplier.contract_end_date,
        renewal_notification_days=supplier.renewal_notification_days,
        status=supplier.status,
        is_active=supplier.is_active,
        created_at=supplier.created_at.isoformat(),
        updated_at=supplier.updated_at.isoformat(),
    )


@router.get("/", response_model=list[SupplierResponse])
def list_suppliers(user: User = Depends(get_current_user)):
    """Obtiene la lista de todos los proveedores activos."""
    suppliers = Supplier.objects.filter(is_active=True)
    return [_serialize_supplier(s) for s in suppliers]


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: str, user: User = Depends(get_current_user)):
    """Obtiene un proveedor por su ID."""
    try:
        supplier = Supplier.objects.get(id=supplier_id, is_active=True)
    except Supplier.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )
    return _serialize_supplier(supplier)


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(body: SupplierCreate, user: User = Depends(get_current_user)):
    """Crea un nuevo proveedor."""
    try:
        supplier = Supplier.objects.create(**body.model_dump())
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _serialize_supplier(supplier)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: str,
    body: SupplierUpdate,
    user: User = Depends(get_current_user),
):
    """Actualiza los datos de un proveedor existente."""
    try:
        supplier = Supplier.objects.get(id=supplier_id, is_active=True)
    except Supplier.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(supplier, field, value)
    try:
        supplier.full_clean()
        supplier.save()
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return _serialize_supplier(supplier)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: str, user: User = Depends(get_current_user)):
    """Elimina (desactiva) un proveedor de forma lógica."""
    try:
        supplier = Supplier.objects.get(id=supplier_id, is_active=True)
    except Supplier.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proveedor no encontrado",
        )
    supplier.is_active = False
    supplier.save()
