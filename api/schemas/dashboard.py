from pydantic import BaseModel
from datetime import date


class ClientesNuevosItem(BaseModel):
    periodo: str
    cantidad: int


class ClientesNuevosResponse(BaseModel):
    total: int
    datos: list[ClientesNuevosItem]


class ClientesPorEstadoItem(BaseModel):
    estado: str
    cantidad: int


class ClientesPorEstadoResponse(BaseModel):
    total: int
    datos: list[ClientesPorEstadoItem]


class ClientesPorPlanItem(BaseModel):
    tipo_plan: str
    cantidad: int
    porcentaje: float


class ClientesPorPlanResponse(BaseModel):
    total: int
    datos: list[ClientesPorPlanItem]


class PagosVencidosItem(BaseModel):
    """Item de pago vencido para el dashboard."""
    usuario: str
    monto: float
    fecha_vencimiento: str
    dias_vencido: int


class PagosVencidosResponse(BaseModel):
    """Resumen de pagos vencidos."""
    cantidad_total: int
    monto_total: float
    datos: list[PagosVencidosItem]
