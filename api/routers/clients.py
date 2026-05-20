"""Router de clientes con operaciones CRUD completas.
Incluye: listado con filtros, creación, detalle, edición y baja lógica.
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.db.models import Q

from api.routers.auth import get_current_user
from api.schemas.clients import (
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from clients.models import AuditLog, Client, WebType, WebFeature, User

router = APIRouter()


def _registrar_auditoria(usuario, accion, modulo, registro_id, detalle=None):
    """Crea un registro en la bitácora de auditoría."""
    AuditLog.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        registro_id=registro_id,
        detalle=detalle or {},
    )


def _client_to_response(client: Client) -> ClientResponse:
    """Convierte un modelo Client a su schema de respuesta ClientResponse."""
    return ClientResponse(
        id=str(client.id),
        cupe=client.cupe or "",
        name=client.name,
        document_type=client.document_type or "",
        document_number=client.document_number,
        email=client.email,
        phone=client.phone,
        web_type=client.web_type.name if client.web_type else None,
        features=[{"id": str(f.id), "name": f.name, "extra_price": str(f.extra_price)} for f in client.features.all()],
        plan=client.plan,
        status=client.status,
        base_price=client.base_price,
        extra_price=client.extra_price,
        total_price=client.total_price,
        initial_payment=client.initial_payment,
        domain_price=client.domain_price,
        payment_frequency=client.payment_frequency,
        registration_date=client.registration_date,
        delivery_date=client.delivery_date,
        next_payment_date=client.next_payment_date,
        notes=client.notes or "",
        created_by=client.created_by.username if client.created_by else None,
        is_active=client.is_active,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get("/", response_model=ClientListResponse)
def list_clients(
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=100),
    status: str | None = None,
    plan: str | None = None,
    web_type_id: str | None = None,
    payment_frequency: str | None = None,
    is_active: bool | None = None,
    ordering: str = Query("-created_at", description="Campo para ordenar. Prefijo - para descendente."),
):
    """
    Listado de clientes con filtros múltiples, paginación, búsqueda y ordenamiento.
    - Filtros: status, plan, web_type_id, payment_frequency, is_active
    - Búsqueda: nombre, CUPE, documento, email, teléfono
    - Paginación real con offset/limit
    - Ordenamiento por cualquier campo (name, email, created_at, etc.)
    """
    filters = Q()
    if search:
        filters &= (
            Q(name__icontains=search)
            | Q(cupe__icontains=search)
            | Q(document_number__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )
    if status:
        filters &= Q(status=status)
    if plan:
        filters &= Q(plan=plan)
    if web_type_id:
        filters &= Q(web_type_id=web_type_id)
    if payment_frequency:
        filters &= Q(payment_frequency=payment_frequency)
    if is_active is not None:
        filters &= Q(is_active=is_active)

    qs = Client.objects.filter(filters).select_related("web_type", "created_by").prefetch_related("features").order_by(ordering)
    total = qs.count()
    offset = (page - 1) * page_size
    clients = qs[offset : offset + page_size]

    return ClientListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=[_client_to_response(c) for c in clients],
    )


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(body: ClientCreate, user: User = Depends(get_current_user)):
    """Crea un nuevo cliente con validaciones y cálculos automáticos."""
    # Validar unicidad de documento
    if Client.objects.filter(document_number=body.document_number).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de documento ya está registrado",
        )

    # Validar unicidad de email
    if Client.objects.filter(email=body.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado",
        )

    data = body.model_dump()
    feature_ids = data.pop("feature_ids", [])
    web_type_id = data.pop("web_type_id", None)

    web_type = None
    if web_type_id:
        try:
            web_type = WebType.objects.get(id=web_type_id, is_active=True)
        except WebType.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de web no encontrado")

    client = Client(
        **data,
        web_type=web_type,
        created_by=user,
    )
    client.save()

    if web_type:
        base = web_type.base_price_rent if client.plan == "alquiler" else web_type.base_price_sale
        client.base_price = base
        client.total_price = base
        client.save(update_fields=["base_price", "total_price"])

    if feature_ids:
        features = WebFeature.objects.filter(id__in=feature_ids, is_active=True)
        client.features.set(features)
        client.update_prices()

    _registrar_auditoria(
        usuario=user,
        accion="creacion",
        modulo="clients",
        registro_id=str(client.id),
        detalle={"name": client.name, "document_number": client.document_number, "email": client.email},
    )

    return _client_to_response(client)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: str, user: User = Depends(get_current_user)):
    """Obtiene el detalle completo de un cliente por su ID."""
    try:
        client = Client.objects.select_related("web_type", "created_by").prefetch_related("features").get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return _client_to_response(client)


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(client_id: str, body: ClientUpdate, user: User = Depends(get_current_user)):
    """Actualiza un cliente con recálculo automático de precios y fechas."""
    try:
        client = Client.objects.select_related("web_type").prefetch_related("features").get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    data = body.model_dump(exclude_unset=True)
    feature_ids = data.pop("feature_ids", None)
    web_type_id = data.pop("web_type_id", None)

    if web_type_id is not None:
        try:
            web_type = WebType.objects.get(id=web_type_id, is_active=True)
        except WebType.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de web no encontrado")
        client.web_type = web_type
        base = web_type.base_price_rent if client.plan == "alquiler" else web_type.base_price_sale
        client.base_price = base

    if "delivery_date" in data and data["delivery_date"] and client.status == "en_desarrollo":
        client.status = "activo"
        if client.payment_frequency == "mensual":
            client.next_payment_date = data["delivery_date"] + timedelta(days=30)
        else:
            client.next_payment_date = date(data["delivery_date"].year + 1, data["delivery_date"].month, data["delivery_date"].day)

    for attr, value in data.items():
        setattr(client, attr, value)

    client.save()

    if feature_ids is not None:
        features = WebFeature.objects.filter(id__in=feature_ids, is_active=True)
        client.features.set(features)
        client.update_prices()

    _registrar_auditoria(
        usuario=user,
        accion="actualizacion",
        modulo="clients",
        registro_id=client_id,
        detalle={"campos_actualizados": list(body.model_dump(exclude_unset=True).keys())},
    )

    return _client_to_response(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: str, user: User = Depends(get_current_user)):
    """Eliminación lógica de cliente: marca is_active=False y status=inactivo."""
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    _registrar_auditoria(
        usuario=user,
        accion="eliminacion",
        modulo="clients",
        registro_id=client_id,
        detalle={"name": client.name, "document_number": client.document_number},
    )

    client.is_active = False
    client.status = "inactivo"
    client.save()
