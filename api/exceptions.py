# Excepciones personalizadas para errores funcionales, técnicos y de permisos — RF-37-T01
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Error base del sistema. Todos los errores personalizados heredan de acá."""

    def __init__(self, detail: str, code: int, field: str | None = None):
        super().__init__(status_code=code, detail=detail)
        self.code = code
        self.field = field


class FunctionalError(AppException):
    """Error funcional: datos inválidos, reglas de negocio, duplicados."""

    def __init__(self, detail: str, field: str | None = None):
        super().__init__(detail=detail, code=status.HTTP_400_BAD_REQUEST, field=field)


class NotFoundError(AppException):
    """Error de recurso no encontrado."""

    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(detail=detail, code=status.HTTP_404_NOT_FOUND)


class AuthError(AppException):
    """Error de autenticación: token inválido, credenciales incorrectas."""

    def __init__(self, detail: str = "No autorizado"):
        super().__init__(detail=detail, code=status.HTTP_401_UNAUTHORIZED)


class PermissionError(AppException):
    """Error de permisos: el usuario no tiene acceso al recurso."""

    def __init__(self, detail: str = "Permiso denegado"):
        super().__init__(detail=detail, code=status.HTTP_403_FORBIDDEN)


class TechnicalError(AppException):
    """Error técnico: error interno del servidor, base de datos caída, etc."""

    def __init__(self, detail: str = "Error interno del servidor"):
        super().__init__(detail=detail, code=status.HTTP_500_INTERNAL_SERVER_ERROR)
