from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class UserCreateRequest(BaseModel):
    """Esquema para registrar un nuevo colaborador con datos personales y credenciales"""
    username: str  # Nombre de usuario para inicio de sesión
    password: str  # Contraseña que será hasheada con bcrypt
    email: str = ""  # Correo electrónico del colaborador
    first_name: str = ""  # Nombre del colaborador
    last_name: str = ""  # Apellido del colaborador
    role_id: Optional[str] = None  # Identificador del rol asignado
    document_number: Optional[str] = None  # Número de documento único (INE, RFC, etc.)
    phone: str = ""  # Teléfono de contacto del colaborador
    area: str = ""  # Área o departamento al que pertenece
    hire_date: Optional[date] = None  # Fecha de contratación del colaborador
    notes: str = ""  # Notas adicionales sobre el colaborador


class UserUpdateRequest(BaseModel):
    """Esquema para editar datos de un colaborador"""
    username: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[str] = None
    is_active: Optional[bool] = None
    phone: Optional[str] = None
    area: Optional[str] = None
    document_number: Optional[str] = None
    hire_date: Optional[date] = None
    notes: Optional[str] = None


class UserResponse(BaseModel):
    """Respuesta completa de un colaborador incluyendo datos del perfil"""
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = None
    role_id: Optional[str] = None
    is_active: bool
    is_staff: bool
    phone: str = ""  # Teléfono de contacto del colaborador
    area: str = ""  # Área o departamento al que pertenece
    document_number: Optional[str] = None  # Número de documento único del colaborador
    cupe: str = ""  # Identificador CUPE generado automáticamente
    hire_date: Optional[date] = None  # Fecha de contratación
    notes: str = ""  # Notas adicionales
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
