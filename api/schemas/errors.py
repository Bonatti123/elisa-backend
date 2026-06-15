# RF-37-T01: Esquemas de respuesta estandarizados para errores
# Define la estructura única que sigue toda respuesta de error en la API.
# Esto garantiza que el frontend siempre reciba el mismo formato y pueda
# mostrar los mensajes de forma consistente.
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Formato único para errores funcionales, técnicos y de permisos.
    - detail: mensaje legible para el usuario
    - code: código HTTP del error
    - field: (opcional) nombre del campo que causó el error
    """
    detail: str
    code: int
    field: Optional[str] = None


class ValidationErrorDetail(BaseModel):
    """Detalle de un error de validación individual."""
    field: str
    detail: str


class ValidationErrorResponse(BaseModel):
    """Respuesta para errores de validación (422).
    Incluye una lista de errores con el campo y el mensaje específico."""
    detail: str = "Error de validación"
    code: int = 422
    errors: list[ValidationErrorDetail]
