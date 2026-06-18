import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.db.models import Q

from api.schemas.users import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
)
from api.routers.auth import get_current_user
from clients.models import User, Role, Collaborator

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreateRequest, current_user: User = Depends(get_current_user)):
    """Registrar un nuevo colaborador con hash bcrypt y creación del perfil Collaborator"""
    # Solo el personal autorizado (staff) puede crear colaboradores
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    # Validar que el username no esté duplicado antes de crear
    if User.objects.filter(username=body.username).exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El username ya existe")

    # Validar que el email no esté duplicado si se proporcionó
    if body.email and User.objects.filter(email=body.email).exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya existe")

    # Validar que el document_number no esté duplicado si se proporcionó
    if body.document_number and Collaborator.objects.filter(document_number=body.document_number).exists():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El número de documento ya existe")

    # Validar y asignar el rol si se proporcionó
    role = None
    if body.role_id:
        try:
            role = Role.objects.get(id=body.role_id, is_active=True)
        except Role.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")

    # Crear el usuario con hash bcrypt mediante set_password de Django
    user = User(
        username=body.username,
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        role=role,
    )
    user.set_password(body.password)  # Hash bcrypt automático
    user.save()

    # Crear el perfil Collaborator vinculado al usuario
    collaborator = Collaborator(
        user=user,
        phone=body.phone,
        area=body.area,
        document_number=body.document_number,
        hire_date=body.hire_date,
        notes=body.notes,
    )
    collaborator.save()  # El CUPE se genera automáticamente en el método save

    return _user_to_response(user)


@router.get("/users", response_model=UserListResponse)
def list_users(
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),  # Número de página para paginación
    page_size: int = Query(20, ge=1, le=100),  # Cantidad de resultados por página
    search: str = Query("", max_length=100),  # Término de búsqueda por nombre, email o username
    is_active: bool | None = None,  # Filtrar por estado activo/inactivo del colaborador
    role_id: str | None = None,  # Filtrar por rol específico
):
    """Listar colaboradores con paginación, búsqueda y filtro opcional por is_active"""
    # Solo el personal autorizado puede listar colaboradores
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    # Construir filtros dinámicos según los parámetros de consulta recibidos
    filters = Q()
    if search:  # Búsqueda por username, nombre, apellido o email
        filters &= Q(username__icontains=search) | Q(
            first_name__icontains=search
        ) | Q(last_name__icontains=search) | Q(email__icontains=search)
    if is_active is not None:  # Filtro opcional por estado activo o inactivo
        filters &= Q(is_active=is_active)
    if role_id:  # Filtro opcional por rol
        filters &= Q(role_id=role_id)

    # Ejecutar consulta con filtros y relaciones para evitar consultas N+1
    queryset = User.objects.filter(filters).select_related("role", "collaborator_profile").order_by("username")
    total = queryset.count()  # Total de resultados para la paginación

    # Paginar resultados usando offset/limit
    offset = (page - 1) * page_size
    users = queryset[offset : offset + page_size]

    return UserListResponse(
        count=total,
        next=None,
        previous=None,
        results=[_user_to_response(u) for u in users],
    )


@router.get("/users/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Devuelve los datos completos del colaborador autenticado incluyendo perfil Collaborator"""
    # Recargar el usuario con relaciones incluidas para obtener el perfil completo
    user = User.objects.select_related("role", "collaborator_profile").get(id=current_user.id)
    return _user_to_response(user)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Ver detalle de un colaborador por su ID incluyendo datos del perfil Collaborator"""
    # El usuario puede ver su propio perfil; el staff puede ver cualquier perfil
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    try:
        # Buscar el usuario con relaciones incluidas para evitar consultas adicionales
        user = User.objects.select_related("role", "collaborator_profile").get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    return _user_to_response(user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str, body: UserUpdateRequest, current_user: User = Depends(get_current_user)
):
    """Editar datos del colaborador incluyendo contraseña, rol y perfil Collaborator"""
    # El usuario puede editar su propio perfil; el staff puede editar cualquier perfil
    if not current_user.is_staff and str(current_user.id) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")

    try:
        # Buscar el usuario con relaciones incluidas para edición
        user = User.objects.select_related("role", "collaborator_profile").get(id=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    # Obtener o crear el perfil Collaborator si no existe
    profile, _ = Collaborator.objects.get_or_create(user=user)

    # Actualizar solo los campos del usuario que vienen en la solicitud
    if body.username is not None:  # Cambiar nombre de usuario
        if User.objects.filter(username=body.username).exclude(id=user_id).exists():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El username ya existe")
        user.username = body.username
    if body.email is not None:  # Cambiar correo electrónico
        if body.email and User.objects.filter(email=body.email).exclude(id=user_id).exists():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El email ya existe")
        user.email = body.email
    if body.first_name is not None:  # Cambiar nombre
        user.first_name = body.first_name
    if body.last_name is not None:  # Cambiar apellido
        user.last_name = body.last_name
    if body.password is not None:  # Cambiar contraseña con hash bcrypt
        user.set_password(body.password)
    if body.is_active is not None:  # Cambiar estado del colaborador
        if not current_user.is_staff:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
        if body.is_active is False and user.is_superuser:  # Verificar que no sea el último superadmin activo
            _check_last_superadmin(user)
        user.is_active = body.is_active
    if body.role_id is not None:  # Cambiar rol del colaborador
        if not current_user.is_staff:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")
        try:
            role = Role.objects.get(id=body.role_id, is_active=True)
        except Role.DoesNotExist:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
        user.role = role

    user.save()

    # Actualizar los campos del perfil Collaborator si vienen en la solicitud
    if body.phone is not None:  # Actualizar teléfono de contacto
        profile.phone = body.phone
    if body.area is not None:  # Actualizar área o departamento
        profile.area = body.area
    if body.document_number is not None:  # Actualizar número de documento
        if body.document_number and Collaborator.objects.filter(document_number=body.document_number).exclude(pk=profile.pk).exists():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El número de documento ya existe")
        profile.document_number = body.document_number
    if body.hire_date is not None:  # Actualizar fecha de contratación
        profile.hire_date = body.hire_date
    if body.notes is not None:  # Actualizar notas adicionales
        profile.notes = body.notes

    profile.save()

    return _user_to_response(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Dar de baja lógica a un colaborador estableciendo is_active=False"""
    # Solo el personal autorizado (staff) puede dar de baja a otros colaboradores
    if not current_user.is_staff:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo personal autorizado")

    try:
        user = User.objects.get(id=user_id)  # Buscar el colaborador por su ID único
    except User.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Colaborador no encontrado")

    # Evitar que el usuario se dé de baja a sí mismo por seguridad
    if str(user.id) == str(current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No puedes darte de baja a ti mismo")

    # Verificar que no se esté desactivando al último superadmin activo del sistema
    if user.is_superuser:
        _check_last_superadmin(user)

    user.is_active = False  # Marcar como inactivo en lugar de eliminar el registro
    user.save()
    return None  # Respuesta 204 No Content sin cuerpo


def _check_last_superadmin(user: User):
    """Valida que no se esté desactivando al único superadmin activo del sistema"""
    superadmins_activos = User.objects.filter(is_superuser=True, is_active=True).count()
    if superadmins_activos <= 1:  # Si solo queda un superadmin activo, no se permite desactivarlo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede desactivar al único superadmin activo del sistema"
        )


def _get_collaborator_profile(user: User):
    """Obtiene el perfil Collaborator del usuario o None si no existe"""
    try:
        return user.collaborator_profile
    except Collaborator.DoesNotExist:
        return None


def _user_to_response(user: User) -> UserResponse:
    """Convierte un modelo User de Django al esquema de respuesta incluyendo datos del perfil Collaborator"""
    profile = _get_collaborator_profile(user)
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
        phone=profile.phone if profile else "",
        area=profile.area if profile else "",
        document_number=profile.document_number if profile else None,
        cupe=profile.cupe if profile else "",
        hire_date=profile.hire_date if profile else None,
        notes=profile.notes if profile else "",
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
