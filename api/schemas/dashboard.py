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
