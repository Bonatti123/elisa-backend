from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncYear

from api.schemas.dashboard import (
    ClientesNuevosItem,
    ClientesNuevosResponse,
    ClientesPorEstadoItem,
    ClientesPorEstadoResponse,
    ClientesPorPlanItem,
    ClientesPorPlanResponse,
)
from clients.models import User
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
