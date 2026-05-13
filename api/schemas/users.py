from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreateRequest(BaseModel):
    """Esquema para registrar un nuevo colaborador"""
    username: str
    password: str
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    role_id: Optional[str] = None


class UserUpdateRequest(BaseModel):
    """Esquema para editar datos de un colaborador"""
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Respuesta completa de un colaborador"""
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = None
    role_id: Optional[str] = None
    is_active: bool
    is_staff: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Respuesta paginada del listado de colaboradores"""
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[UserResponse]


class RoleResponse(BaseModel):
    """Respuesta de un rol del sistema"""
    id: str
    name: str
    description: str
    is_active: bool
