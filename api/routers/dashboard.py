from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth, TruncYear

from api.schemas.dashboard import (
    ClientesNuevosItem,
    ClientesNuevosResponse,
    ClientesPorEstadoItem,
    ClientesPorEstadoResponse,
    ClientesPorPlanItem,
    ClientesPorPlanResponse,
    PagosVencidosItem,
    PagosVencidosResponse,
)
from clients.models import User, Payment
from api.routers.auth import get_current_user

router = APIRouter()


@router.get(
    "/clientes-nuevos",
    response_model=ClientesNuevosResponse,
    summary="Clientes nuevos por período",
    description="Retorna la cantidad de clientes nuevos agrupados por mes o año.",
)
def clientes_nuevos(
    periodo: str = Query("mensual", pattern="^(mensual|anual)$"),
    desde: date | None = None,
    hasta: date | None = None,
    user=Depends(get_current_user),
):
    """Retorna la métrica de clientes nuevos agrupados por período."""
    filters = Q()
    if desde:
        filters &= Q(created_at__date__gte=desde)
    if hasta:
        filters &= Q(created_at__date__lte=hasta)

    if periodo == "anual":
        qs = (
            User.objects.filter(filters)
            .annotate(periodo=TruncYear("created_at"))
            .values("periodo")
            .annotate(cantidad=Count("id"))
            .order_by("periodo")
        )
    else:
        qs = (
            User.objects.filter(filters)
            .annotate(periodo=TruncMonth("created_at"))
            .values("periodo")
            .annotate(cantidad=Count("id"))
            .order_by("periodo")
        )

    datos = [
        ClientesNuevosItem(
            periodo=str(item["periodo"].strftime("%Y-%m") if item["periodo"] else ""),
            cantidad=item["cantidad"],
        )
        for item in qs
    ]
    total = sum(item.cantidad for item in datos)

    return ClientesNuevosResponse(total=total, datos=datos)


@router.get(
    "/clientes-por-estado",
    response_model=ClientesPorEstadoResponse,
    summary="Clientes por estado",
    description="Retorna la cantidad de clientes agrupados por estado (activo, inactivo, en_desarrollo).",
)
def clientes_por_estado(
    user=Depends(get_current_user),
):
    """Retorna la métrica de clientes agrupados por estado."""
    qs = (
        User.objects.values("status")
        .annotate(cantidad=Count("id"))
        .order_by("status")
    )

    datos = [
        ClientesPorEstadoItem(
            estado=item["status"],
            cantidad=item["cantidad"],
        )
        for item in qs
    ]
    total = sum(item.cantidad for item in datos)

    return ClientesPorEstadoResponse(total=total, datos=datos)


@router.get(
    "/clientes-por-plan",
    response_model=ClientesPorPlanResponse,
    summary="Clientes por tipo de plan",
    description="Retorna la distribución de clientes por tipo de plan (alquiler vs venta) con porcentaje.",
)
def clientes_por_plan(
    user=Depends(get_current_user),
):
    """Retorna la métrica de clientes distribuidos por tipo de plan."""
    total_clientes = User.objects.filter(plan__isnull=False).count()

    qs = (
        User.objects.filter(plan__isnull=False)
        .values("plan__tipo")
        .annotate(cantidad=Count("id"))
        .order_by("plan__tipo")
    )

    datos = [
        ClientesPorPlanItem(
            tipo_plan=item["plan__tipo"],
            cantidad=item["cantidad"],
            porcentaje=round((item["cantidad"] / total_clientes) * 100, 2) if total_clientes else 0,
        )
        for item in qs
    ]
    total = sum(item.cantidad for item in datos)

    return ClientesPorPlanResponse(total=total, datos=datos)


@router.get(
    "/pagos-vencidos",
    response_model=PagosVencidosResponse,
    summary="Pagos vencidos",
    description="Retorna el monto total y la cantidad de pagos vencidos con detalle.",
)
def pagos_vencidos(
    user=Depends(get_current_user),
):
    """Retorna la métrica de pagos vencidos con monto y cantidad."""
    hoy = datetime.now(timezone.utc).date()
    qs = Payment.objects.filter(
        estado="vencido",
        fecha_vencimiento__lt=hoy,
    ).select_related("user")

    datos = [
        PagosVencidosItem(
            usuario=item.user.username,
            monto=float(item.monto),
            fecha_vencimiento=item.fecha_vencimiento.isoformat(),
            dias_vencido=(hoy - item.fecha_vencimiento).days,
        )
        for item in qs
    ]

    monto_total = sum(item.monto for item in datos)
    cantidad_total = len(datos)

    return PagosVencidosResponse(
        cantidad_total=cantidad_total,
        monto_total=monto_total,
        datos=datos,
    )
