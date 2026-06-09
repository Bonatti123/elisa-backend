"""#BE028: Router de contabilidad con operaciones CRUD de compras, ventas y resumen financiero.
Todos los endpoints requieren permisos de administrador (is_staff).
Incluye control de partida doble, bloqueo preventivo y auditoría inmutable.
"""

from datetime import date
from typing import Any

from django.db import transaction
from django.db.models import Sum
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.routers.auth import get_current_user
from api.schemas.accounting import (
    FinancialSummaryResponse,
    PurchaseCreate,
    PurchaseResponse,
    PurchaseUpdate,
    SaleCreate,
    SaleResponse,
    SaleUpdate,
)
from clients.models import AccountingEntryHistory, Purchase, Sale, User

router = APIRouter()

CURRENT_YEAR = date.today().year


# ─── FUNCIONES AUXILIARES ──────────────────────────────────────────────
# #BE029: Helpers de transformación y control de acceso


def require_staff(user: User = Depends(get_current_user)) -> User:
    """#BE029: Dependencia que verifica que el usuario tenga permisos de staff."""
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return user


def registrar_historial(
    transaction_type: str,
    transaction_id: str,
    action: str,
    user_id: str,
    old_data: dict[str, Any] | None = None,
    new_data: dict[str, Any] | None = None,
) -> None:
    """#BE042: Persiste un registro inmutable en la bitácora de auditoría contable."""
    AccountingEntryHistory.objects.create(
        transaction_type=transaction_type,
        transaction_id=transaction_id,
        action=action,
        old_data=old_data or {},
        new_data=new_data or {},
        user_id=user_id,
    )


def validar_rango_fechas(date_from: date | None, date_to: date | None) -> None:
    """#BE038: Valida que la fecha inicial no sea posterior a la fecha final."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha inicial no puede ser posterior a la fecha final",
        )


def validar_anio_periodo(period_year: int) -> None:
    """#BE039: Valida que el año del período esté dentro de un rango razonable."""
    if period_year < 2000 or period_year > CURRENT_YEAR + 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El año del período ({period_year}) está fuera del rango permitido "
            f"(2000 - {CURRENT_YEAR + 10})",
        )


def purchase_to_dict(purchase: Purchase) -> dict[str, Any]:
    """#BE040: Convierte una compra a diccionario para el historial de auditoría."""
    return {
        "id": str(purchase.id),
        "provider_name": purchase.provider_name,
        "document_type": purchase.document_type,
        "document_number": purchase.document_number,
        "amount": str(purchase.amount),
        "issue_date": str(purchase.issue_date),
        "category": purchase.category,
        "notes": purchase.notes,
        "is_active": purchase.is_active,
    }


def sale_to_dict(sale: Sale) -> dict[str, Any]:
    """#BE041: Convierte una venta a diccionario para el historial de auditoría."""
    return {
        "id": str(sale.id),
        "client_name": sale.client_name,
        "client_email": sale.client_email,
        "document_type": sale.document_type,
        "document_number": sale.document_number,
        "amount": str(sale.amount),
        "issue_date": str(sale.issue_date),
        "status": sale.status,
        "category": sale.category,
        "notes": sale.notes,
        "is_active": sale.is_active,
    }


# ─── COMPRAS ─────────────────────────────────────────────────────────
# #BE030: Endpoints CRUD de compras con blindaje atómico y auditoría


@router.get("/purchases/", response_model=list[PurchaseResponse])
def list_purchases(
    provider_name: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_staff),
) -> list[PurchaseResponse]:
    """#BE031: Lista todas las compras activas con filtros por proveedor, tipo, categoría y fechas."""
    validar_rango_fechas(date_from, date_to)
    qs = Purchase.objects.filter(is_active=True)
    if provider_name:
        qs = qs.filter(provider_name__icontains=provider_name)
    if document_type:
        qs = qs.filter(document_type=document_type)
    if category:
        qs = qs.filter(category__icontains=category)
    if date_from:
        qs = qs.filter(issue_date__gte=date_from)
    if date_to:
        qs = qs.filter(issue_date__lte=date_to)
    qs = qs.order_by("-issue_date", "-created_at")[skip : skip + limit]
    return list(qs)


@router.get("/purchases/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(
    purchase_id: str,
    _: User = Depends(require_staff),
) -> PurchaseResponse:
    """#BE032: Obtiene el detalle de una compra por su ID."""
    try:
        purchase = Purchase.objects.get(id=purchase_id, is_active=True)
    except Purchase.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada",
        )
    return purchase


@router.post(
    "/purchases/",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    body: PurchaseCreate,
    user: User = Depends(require_staff),
) -> PurchaseResponse:
    """#BE033: Registra una nueva compra con validación de monto y registro de auditoría."""
    with transaction.atomic():
        purchase = Purchase.objects.create(**body.model_dump())
        registrar_historial(
            transaction_type="purchase",
            transaction_id=str(purchase.id),
            action="creado",
            user_id=str(user.id),
            new_data=purchase_to_dict(purchase),
        )
    return purchase


@router.put("/purchases/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(
    purchase_id: str,
    body: PurchaseUpdate,
    user: User = Depends(require_staff),
) -> PurchaseResponse:
    """#BE034: Actualiza una compra con bloqueo preventivo y registro de historial."""
    with transaction.atomic():
        try:
            purchase = Purchase.objects.select_for_update().get(id=purchase_id, is_active=True)
        except Purchase.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra no encontrada",
            )
        old_data = purchase_to_dict(purchase)
        data = body.model_dump(exclude_unset=True)
        for attr, value in data.items():
            setattr(purchase, attr, value)
        purchase.save()
        registrar_historial(
            transaction_type="purchase",
            transaction_id=str(purchase.id),
            action="editado",
            user_id=str(user.id),
            old_data=old_data,
            new_data=purchase_to_dict(purchase),
        )
    return purchase


@router.delete("/purchases/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(
    purchase_id: str,
    user: User = Depends(require_staff),
) -> None:
    """#BE035: Eliminación lógica de una compra. Marca is_active=False y registra auditoría."""
    with transaction.atomic():
        try:
            purchase = Purchase.objects.select_for_update().get(id=purchase_id, is_active=True)
        except Purchase.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Compra no encontrada",
            )
        old_data = purchase_to_dict(purchase)
        purchase.is_active = False
        purchase.save()
        registrar_historial(
            transaction_type="purchase",
            transaction_id=str(purchase.id),
            action="cancelado",
            user_id=str(user.id),
            old_data=old_data,
            new_data=purchase_to_dict(purchase),
        )


# ─── VENTAS ──────────────────────────────────────────────────────────
# #BE036: Endpoints CRUD de ventas con blindaje atómico y auditoría


@router.get("/sales/", response_model=list[SaleResponse])
def list_sales(
    client_name: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    category: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_staff),
) -> list[SaleResponse]:
    """#BE037: Lista todas las ventas activas con filtros por cliente, tipo, estado, categoría y fechas."""
    validar_rango_fechas(date_from, date_to)
    qs = Sale.objects.filter(is_active=True)
    if client_name:
        qs = qs.filter(client_name__icontains=client_name)
    if document_type:
        qs = qs.filter(document_type=document_type)
    if status_filter:
        qs = qs.filter(status=status_filter)
    if category:
        qs = qs.filter(category__icontains=category)
    if date_from:
        qs = qs.filter(issue_date__gte=date_from)
    if date_to:
        qs = qs.filter(issue_date__lte=date_to)
    qs = qs.order_by("-issue_date", "-created_at")[skip : skip + limit]
    return list(qs)


@router.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: str,
    _: User = Depends(require_staff),
) -> SaleResponse:
    """#BE038: Obtiene el detalle de una venta por su ID."""
    try:
        sale = Sale.objects.get(id=sale_id, is_active=True)
    except Sale.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada",
        )
    return sale


@router.post(
    "/sales/",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    body: SaleCreate,
    user: User = Depends(require_staff),
) -> SaleResponse:
    """#BE039: Registra una nueva venta con validación de monto y registro de auditoría."""
    with transaction.atomic():
        sale = Sale.objects.create(**body.model_dump())
        registrar_historial(
            transaction_type="sale",
            transaction_id=str(sale.id),
            action="creado",
            user_id=str(user.id),
            new_data=sale_to_dict(sale),
        )
    return sale


@router.put("/sales/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: str,
    body: SaleUpdate,
    user: User = Depends(require_staff),
) -> SaleResponse:
    """#BE040: Actualiza una venta con bloqueo preventivo y registro de historial."""
    with transaction.atomic():
        try:
            sale = Sale.objects.select_for_update().get(id=sale_id, is_active=True)
        except Sale.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venta no encontrada",
            )
        old_data = sale_to_dict(sale)
        data = body.model_dump(exclude_unset=True)
        for attr, value in data.items():
            setattr(sale, attr, value)
        sale.save()
        registrar_historial(
            transaction_type="sale",
            transaction_id=str(sale.id),
            action="editado",
            user_id=str(user.id),
            old_data=old_data,
            new_data=sale_to_dict(sale),
        )
    return sale


@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: str,
    user: User = Depends(require_staff),
) -> None:
    """#BE041: Eliminación lógica de una venta. Marca is_active=False y registra auditoría."""
    with transaction.atomic():
        try:
            sale = Sale.objects.select_for_update().get(id=sale_id, is_active=True)
        except Sale.DoesNotExist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venta no encontrada",
            )
        old_data = sale_to_dict(sale)
        sale.is_active = False
        sale.save()
        registrar_historial(
            transaction_type="sale",
            transaction_id=str(sale.id),
            action="cancelado",
            user_id=str(user.id),
            old_data=old_data,
            new_data=sale_to_dict(sale),
        )


# ─── RESUMEN FINANCIERO ──────────────────────────────────────────────
# #BE042: Endpoint de consolidación financiera con validación de período


@router.get("/financial-summary", response_model=FinancialSummaryResponse)
def financial_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _: User = Depends(require_staff),
) -> FinancialSummaryResponse:
    """#BE043: Resumen financiero con totales de compras, ventas, balance y validación de rango."""
    validar_rango_fechas(date_from, date_to)
    purchases = Purchase.objects.filter(
        is_active=True,
        issue_date__gte=date_from,
        issue_date__lte=date_to,
    )
    sales = Sale.objects.filter(
        is_active=True,
        issue_date__gte=date_from,
        issue_date__lte=date_to,
    )
    total_purchases = purchases.aggregate(total=Sum("amount"))["total"] or 0
    total_sales = sales.aggregate(total=Sum("amount"))["total"] or 0
    return FinancialSummaryResponse(
        total_purchases=total_purchases,
        total_sales=total_sales,
        balance=total_sales - total_purchases,
        purchase_count=purchases.count(),
        sale_count=sales.count(),
        period_start=date_from,
        period_end=date_to,
    )
