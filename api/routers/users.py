import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.db.models import Q

from api.schemas.users import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
)
from api.schemas.auth import UserResponse as AuthUserResponse
from api.routers.auth import get_current_user
from clients.models import User, Role

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreateRequest, current_user: User = Depends(get_current_user)):
    """Registrar un nuevo colaborador en el sistema"""
    # Solo el personal autorizado puede crear colaboradores
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    # Validar que el username no esté duplicado
    if User.objects.filter(username=body.username).exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El username ya existe")

    # Validar y asignar el rol si se proporcionó
    role = None
    if body.role_id:
        try:
            role = Role.objects.get(id=body.role_id, is_active=True)
        except Role.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    # Crear el colaborador con los datos proporcionados
    user = User(
        username=body.username,
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        role=role,
    )
    user.set_password(body.password)
    user.save()

    return _user_to_response(user)


@router.get("/users", response_model=UserListResponse)
def list_users(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", max_length=100),
    is_active: bool | None = None,
    role_id: str | None = None,
):
    """Listar colaboradores con paginación, búsqueda y filtros"""
    # Solo el personal autorizado puede listar colaboradores
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    # Construir filtros dinámicos según los parámetros de consulta
    filters = Q()
    if search:
        filters &= Q(username__icontains=search) | Q(
            first_name__icontains=search
        ) | Q(last_name__icontains=search) | Q(email__icontains=search)
    if is_active is not None:
        filters &= Q(is_active=is_active)
    if role_id:
        filters &= Q(role_id=role_id)

    # Ejecutar consulta con filtros y relaciones
    queryset = User.objects.filter(filters).select_related("role").order_by("username")
    total = queryset.count()

    # Paginar resultados
    offset = (page - 1) * page_size
    users = queryset[offset : offset + page_size]

    return UserListResponse(
        count=total,
        next=None,
        previous=None,
        results=[_user_to_response(u) for u in users],
    )


@router.get("/users/me", response_model=AuthUserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Consultar el colaborador autenticado actualmente"""
    return AuthUserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role.name if current_user.role else None,
        is_active=current_user.is_active,
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Ver detalle de un colaborador por su ID"""
    # El usuario puede ver su propio perfil; el staff puede ver cualquier perfil
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    try:
        user = User.objects.select_related("role").get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    return _user_to_response(user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str, body: UserUpdateRequest, current_user: User = Depends(get_current_user)
):
    """Editar los datos de un colaborador"""
    # El usuario puede editar su propio perfil; el staff puede editar cualquier perfil
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    try:
        user = User.objects.select_related("role").get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    # Actualizar solo los campos que vienen en la solicitud
    if body.username is not None:
        if User.objects.filter(username=body.username).exclude(id=user_id).exists():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El username ya existe")
        user.username = body.username
    if body.email is not None:
        user.email = body.email
    if body.first_name is not None:
        user.first_name = body.first_name
    if body.last_name is not None:
        user.last_name = body.last_name
    if body.password is not None:
        user.set_password(body.password)
    if body.is_active is not None:
        if not current_user.is_staff:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
        user.is_active = body.is_active
    if body.role_id is not None:
        if not current_user.is_staff:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
        try:
            role = Role.objects.get(id=body.role_id, is_active=True)
        except Role.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
        user.role = role

    user.save()
    return _user_to_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Dar de baja lógica a un colaborador (is_active=False)"""
    # Solo el personal autorizado puede dar de baja
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    # Evitar que el usuario se dé de baja a sí mismo
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes darte de baja a ti mismo")

    user.is_active = False
    user.save()
    return None


def _user_to_response(user: User) -> UserResponse:
    """Convierte un modelo User de Django al esquema de respuesta UserResponse"""
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role.name if user.role else None,
        role_id=str(user.role.id) if user.role else None,
        is_active=user.is_active,
        is_staff=user.is_staff,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
