# RF-37-T02: Helpers de respuesta para la API
# Funciones utilitarias que garantizan que todas las respuestas
# de la API sigan la misma estructura: { data, message?, pagination? }
# Esto evita que cada endpoint invente su propio formato.
from typing import Optional


def success_response(data, message: Optional[str] = None):
    """Respuesta exitosa estándar con código 200.
    Uso: return success_response(cliente, "Cliente actualizado")"""
    body = {"data": data}
    if message:
        body["message"] = message
    return body


def created_response(data, message: str = "Recurso creado exitosamente"):
    """Respuesta para creación exitosa con código 201.
    Uso: return created_response(cliente)"""
    return {"data": data, "message": message}


def paginated_response(items, total: int, page: int, page_size: int, message: Optional[str] = None):
    """Respuesta paginada con metadatos de paginación.
    Incluye total, page, page_size y total_pages calculado automáticamente.
    Uso: return paginated_response(items, total, page, page_size)"""
    body = {
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0,
        },
    }
    if message:
        body["message"] = message
    return body
