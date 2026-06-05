from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """DTO para la autenticación de usuarios mediante username y password."""

    username: str
    password: str


class RefreshRequest(BaseModel):
    """DTO para solicitar un nuevo token de acceso usando el token refresh."""

    refresh_token: str


class TokenResponse(BaseModel):
    """DTO de respuesta con los tokens de acceso y refresh para autenticación."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RoleInfo(BaseModel):
    """DTO con la información del rol asociado al usuario autenticado."""

    id: str
    name: str
    permissions: dict


class UserResponse(BaseModel):
    """DTO de respuesta con los datos del perfil del usuario autenticado.
    Incluye la información del rol con sus permisos para que el frontend
    pueda determinar la navegación y las acciones permitidas.
    """

    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: RoleInfo | None = None
    is_active: bool


class LogoutResponse(BaseModel):
    """DTO de respuesta para confirmar el cierre de sesión del usuario."""

    message: str
