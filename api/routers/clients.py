"""Clients router with full CRUD operations.
Includes: filtered listing, creation, detail, update, soft delete,
audit history, and change request management.
"""
from typing import TypedDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.db.models import Q

from api.routers.auth import get_current_user, require_write_access
from api.schemas.clients import (
    ChangeRequestCreate,
    ChangeRequestResponse,
    ChangeRequestReview,
    ClientCreate,
    ClientListResponse,
    ClientResponse,
    ClientUpdate,
)
from clients.models import AuditLog, ChangeRequest, Client, WebType, WebFeature, User


router = APIRouter()


class HistoryEntry(TypedDict):
    """Represents a single audit log entry for the client history endpoint."""
    id: str
    accion: str
    detalle: dict
    usuario: str | None
    created_at: str


def _registrar_auditoria(
    usuario: User | None,
    accion: str,
    modulo: str,
    registro_id: str,
    detalle: dict | None = None,
) -> None:
    """Creates an audit log entry for tracking critical changes."""
    AuditLog.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        registro_id=registro_id,
        detalle=detalle or {},
    )


def _client_to_response(client: Client) -> ClientResponse:
    """Converts a Client model instance into its corresponding API response schema."""
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
    ordering: str = Query("-created_at", description="Sort field. Prefix - for descending."),
) -> ClientListResponse:
    """List clients with filters, pagination, search and sorting.

    Supports filtering by status, plan, web type, payment frequency and active state.
    Search is performed on name, CUPE, document number, email and phone.
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
def create_client(
    body: ClientCreate,
    user: User = Depends(require_write_access),
) -> ClientResponse:
    """Create a new client with automatic validations and price calculations.

    Validates document and email uniqueness, assigns CUPE automatically,
    calculates base and total prices based on web type and plan.
    """
    if Client.objects.filter(document_number=body.document_number).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de documento ya está registrado",
        )

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
def get_client(
    client_id: str,
    user: User = Depends(get_current_user),
) -> ClientResponse:
    """Retrieve full client details by ID."""
    try:
        client = Client.objects.select_related("web_type", "created_by").prefetch_related("features").get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return _client_to_response(client)


@router.get("/{client_id}/history")
def get_client_history(
    client_id: str,
    user: User = Depends(get_current_user),
) -> list[HistoryEntry]:
    """Retrieve the audit history for a specific client."""
    try:
        Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    registros = AuditLog.objects.filter(modulo="clients", registro_id=client_id).select_related("usuario").order_by("-created_at")
    return [
        HistoryEntry(
            id=str(r.id),
            accion=r.accion,
            detalle=r.detalle,
            usuario=r.usuario.username if r.usuario else None,
            created_at=r.created_at.isoformat(),
        )
        for r in registros
    ]


@router.get("/{client_id}/change-requests", response_model=list[ChangeRequestResponse])
def list_change_requests(
    client_id: str,
    user: User = Depends(get_current_user),
) -> list[ChangeRequestResponse]:
    """List all change requests for a given client."""
    try:
        Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    requests = ChangeRequest.objects.filter(cliente_id=client_id).select_related("solicitado_por", "revisado_por").order_by("-created_at")
    return [
        ChangeRequestResponse(
            id=str(r.id),
            cliente_id=str(r.cliente_id),
            campo=r.campo,
            valor_anterior=r.valor_anterior,
            valor_nuevo=r.valor_nuevo,
            motivo=r.motivo,
            estado=r.estado,
            solicitado_por=r.solicitado_por.username if r.solicitado_por else None,
            revisado_por=r.revisado_por.username if r.revisado_por else None,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in requests
    ]


@router.post("/{client_id}/change-requests", response_model=ChangeRequestResponse, status_code=status.HTTP_201_CREATED)
def create_change_request(
    client_id: str,
    body: ChangeRequestCreate,
    user: User = Depends(get_current_user),
) -> ChangeRequestResponse:
    """Create a change request for a client sensitive field."""
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    valor_anterior: dict = {}
    if hasattr(client, body.campo):
        valor_anterior = {body.campo: str(getattr(client, body.campo))}

    solicitud = ChangeRequest.objects.create(
        cliente=client,
        campo=body.campo,
        valor_anterior=valor_anterior,
        valor_nuevo={"valor": body.valor_nuevo},
        motivo=body.motivo,
        solicitado_por=user,
    )

    _registrar_auditoria(
        usuario=user,
        accion="creacion",
        modulo="change_requests",
        registro_id=str(solicitud.id),
        detalle={"cliente_id": client_id, "campo": body.campo, "motivo": body.motivo},
    )

    return ChangeRequestResponse(
        id=str(solicitud.id),
        cliente_id=str(solicitud.cliente_id),
        campo=solicitud.campo,
        valor_anterior=solicitud.valor_anterior,
        valor_nuevo=solicitud.valor_nuevo,
        motivo=solicitud.motivo,
        estado=solicitud.estado,
        solicitado_por=user.username,
        revisado_por=None,
        created_at=solicitud.created_at,
        updated_at=solicitud.updated_at,
    )


@router.patch("/change-requests/{request_id}", response_model=ChangeRequestResponse)
def review_change_request(
    request_id: str,
    body: ChangeRequestReview,
    user: User = Depends(get_current_user),
) -> ChangeRequestResponse:
    """Approve or reject a change request (staff only)."""
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de staff para revisar solicitudes",
        )

    try:
        solicitud = ChangeRequest.objects.select_related("cliente").get(id=request_id)
    except ChangeRequest.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")

    if solicitud.estado != "pendiente":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La solicitud ya fue revisada")

    solicitud.estado = body.estado
    solicitud.revisado_por = user
    solicitud.save()

    if body.estado == "aprobado":
        cliente = solicitud.cliente
        valor = solicitud.valor_nuevo.get("valor")
        if valor is not None and hasattr(cliente, solicitud.campo):
            setattr(cliente, solicitud.campo, valor)
            cliente.save()

    _registrar_auditoria(
        usuario=user,
        accion="actualizacion",
        modulo="change_requests",
        registro_id=request_id,
        detalle={"estado": body.estado, "cliente_id": str(solicitud.cliente_id)},
    )

    return ChangeRequestResponse(
        id=str(solicitud.id),
        cliente_id=str(solicitud.cliente_id),
        campo=solicitud.campo,
        valor_anterior=solicitud.valor_anterior,
        valor_nuevo=solicitud.valor_nuevo,
        motivo=solicitud.motivo,
        estado=solicitud.estado,
        solicitado_por=solicitud.solicitado_por.username if solicitud.solicitado_por else None,
        revisado_por=user.username,
        created_at=solicitud.created_at,
        updated_at=solicitud.updated_at,
    )


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: str,
    body: ClientUpdate,
    user: User = Depends(require_write_access),
) -> ClientResponse:
    """Update a client with automatic price recalculation and date updates."""
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
def delete_client(
    client_id: str,
    user: User = Depends(require_write_access),
) -> None:
    """Soft delete a client by setting is_active=False and status=inactivo."""
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
