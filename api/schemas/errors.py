# Esquemas de respuesta estandarizados para errores — RF-37-T01
from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    detail: str
    code: int
    field: Optional[str] = None


class ValidationErrorDetail(BaseModel):
    field: str
    detail: str


class ValidationErrorResponse(BaseModel):
    detail: str = "Error de validación"
    code: int = 422
    errors: list[ValidationErrorDetail]
