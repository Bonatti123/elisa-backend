"""Router de contabilidad con operaciones CRUD de compras, ventas y resumen financiero.
Todos los endpoints requieren permisos de administrador (is_staff).
"""
from datetime import date

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
from clients.models import Purchase, Sale, User

router = APIRouter()


def require_staff(user: User = Depends(get_current_user)) -> User:
    """Dependencia que verifica que el usuario tenga permisos de staff."""
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return user


# ─── COMPRAS ─────────────────────────────────────────────────────────────


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
):
    """Lista todas las compras activas con filtros por proveedor, tipo, categoría y fechas."""
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
):
    """Obtiene el detalle de una compra por su ID."""
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
    _: User = Depends(require_staff),
):
    """Registra una nueva compra (boleta o factura de compra)."""
    purchase = Purchase.objects.create(**body.model_dump())
    return purchase


@router.put("/purchases/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(
    purchase_id: str,
    body: PurchaseUpdate,
    _: User = Depends(require_staff),
):
    """Actualiza los datos de una compra existente."""
    try:
        purchase = Purchase.objects.get(id=purchase_id, is_active=True)
    except Purchase.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada",
        )
    data = body.model_dump(exclude_unset=True)
    for attr, value in data.items():
        setattr(purchase, attr, value)
    purchase.save()
    return purchase


@router.delete("/purchases/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(
    purchase_id: str,
    _: User = Depends(require_staff),
):
    """Eliminación lógica de una compra. Marca is_active=False."""
    try:
        purchase = Purchase.objects.get(id=purchase_id, is_active=True)
    except Purchase.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compra no encontrada",
        )
    purchase.is_active = False
    purchase.save()


# ─── VENTAS ──────────────────────────────────────────────────────────────


@router.get("/sales/", response_model=list[SaleResponse])
def list_sales(
    client_name: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_staff),
):
    """Lista todas las ventas activas con filtros por cliente, tipo, estado, categoría y fechas."""
    qs = Sale.objects.filter(is_active=True)
    if client_name:
        qs = qs.filter(client_name__icontains=client_name)
    if document_type:
        qs = qs.filter(document_type=document_type)
    if status:
        qs = qs.filter(status=status)
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
):
    """Obtiene el detalle de una venta por su ID."""
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
    _: User = Depends(require_staff),
):
    """Registra una nueva venta (boleta o factura de venta)."""
    sale = Sale.objects.create(**body.model_dump())
    return sale


@router.put("/sales/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: str,
    body: SaleUpdate,
    _: User = Depends(require_staff),
):
    """Actualiza los datos de una venta existente."""
    try:
        sale = Sale.objects.get(id=sale_id, is_active=True)
    except Sale.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada",
        )
    data = body.model_dump(exclude_unset=True)
    for attr, value in data.items():
        setattr(sale, attr, value)
    sale.save()
    return sale


@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(
    sale_id: str,
    _: User = Depends(require_staff),
):
    """Eliminación lógica de una venta. Marca is_active=False."""
    try:
        sale = Sale.objects.get(id=sale_id, is_active=True)
    except Sale.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada",
        )
    sale.is_active = False
    sale.save()


# ─── RESUMEN FINANCIERO ──────────────────────────────────────────────────


@router.get("/financial-summary", response_model=FinancialSummaryResponse)
def financial_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    _: User = Depends(require_staff),
):
    """Resumen financiero: total de compras, ventas, balance y cantidades en un período."""
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

    from django.db.models import Sum

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
