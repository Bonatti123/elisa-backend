from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek, TruncYear

from api.schemas.dashboard import (
    ClientesNuevosItem,
    ClientesNuevosResponse,
    ClientesPorEstadoItem,
    ClientesPorEstadoResponse,
    ClientesPorPlanItem,
    ClientesPorPlanResponse,
    PagosVencidosItem,
    PagosVencidosResponse,
    ReporteItem,
    ReporteResponse,
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

    return PagosVencidosResponse(
        cantidad_total=cantidad_total,
        monto_total=monto_total,
        datos=datos,
    )


@router.get(
    "/reportes",
    response_model=ReporteResponse,
    summary="Reportes por período",
    description="Retorna la agregación de clientes nuevos y pagos agrupados por día, semana o mes.",
)
def reportes(
    tipo_periodo: str = Query("mensual", pattern="^(diario|semanal|mensual)$"),
    desde: date | None = None,
    hasta: date | None = None,
    user=Depends(get_current_user),
):
    """Retorna reportes agregados por día, semana o mes."""
    filtros = Q()
    if desde:
        filtros &= Q(created_at__date__gte=desde)
    if hasta:
        filtros &= Q(created_at__date__lte=hasta)

    # Mapeo del tipo de truncamiento según el período solicitado
    if tipo_periodo == "diario":
        truncar = TruncDay("created_at")
        formato = "%Y-%m-%d"
    elif tipo_periodo == "semanal":
        truncar = TruncWeek("created_at")
        formato = "%Y-%W"
    else:
        truncar = TruncMonth("created_at")
        formato = "%Y-%m"

    # Agregación de usuarios (clientes nuevos) por período
    usuarios_qs = (
        User.objects.filter(filtros)
        .annotate(periodo=truncar)
        .values("periodo")
        .annotate(cantidad=Count("id"))
        .order_by("periodo")
    )

    # Agregación de pagos por período
    pagos_qs = (
        Payment.objects.filter(filtros, estado="pagado")
        .annotate(periodo=truncar)
        .values("periodo")
        .annotate(
            cantidad=Count("id"),
            monto=Sum("monto"),
        )
        .order_by("periodo")
    )

    # Combinar usuarios y pagos en un solo diccionario por período
    datos_por_periodo: dict[str, dict] = {}

    for item in usuarios_qs:
        clave = item["periodo"].strftime(formato) if item["periodo"] else ""
        datos_por_periodo[clave] = {
            "clientes_nuevos": item["cantidad"],
            "pagos_realizados": 0,
            "monto_pagos": 0.0,
        }

    for item in pagos_qs:
        clave = item["periodo"].strftime(formato) if item["periodo"] else ""
        if clave in datos_por_periodo:
            datos_por_periodo[clave]["pagos_realizados"] = item["cantidad"]
            datos_por_periodo[clave]["monto_pagos"] = float(item["monto"] or 0)
        else:
            datos_por_periodo[clave] = {
                "clientes_nuevos": 0,
                "pagos_realizados": item["cantidad"],
                "monto_pagos": float(item["monto"] or 0),
            }

    # Ordenar por período y construir respuesta
    periodos_ordenados = sorted(datos_por_periodo.keys())
    datos = [
        ReporteItem(
            periodo=p,
            clientes_nuevos=datos_por_periodo[p]["clientes_nuevos"],
            pagos_realizados=datos_por_periodo[p]["pagos_realizados"],
            monto_pagos=datos_por_periodo[p]["monto_pagos"],
        )
        for p in periodos_ordenados
    ]

    total_clientes_nuevos = sum(d.clientes_nuevos for d in datos)
    total_pagos = sum(d.pagos_realizados for d in datos)
    total_monto = sum(d.monto_pagos for d in datos)

    return ReporteResponse(
        tipo_periodo=tipo_periodo,
        total_clientes_nuevos=total_clientes_nuevos,
        total_pagos=total_pagos,
        total_monto=total_monto,
        datos=datos,
    )
