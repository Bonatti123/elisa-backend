# Utilidades para respuestas consistentes de la API — RF-37-T02
from typing import Optional


def success_response(data, message: Optional[str] = None):
    """Respuesta exitosa estándar (200)."""
    body = {"data": data}
    if message:
        body["message"] = message
    return body


def created_response(data, message: str = "Recurso creado exitosamente"):
    """Respuesta para creación exitosa (201)."""
    return {"data": data, "message": message}


def paginated_response(items, total: int, page: int, page_size: int, message: Optional[str] = None):
    """Respuesta paginada con metadatos."""
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
