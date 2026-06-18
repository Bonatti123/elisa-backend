# =============================================================================
# Pruebas del módulo de gestión de colaboradores y roles (RF-03)
# Valida el control de acceso basado en jerarquía de roles:
#   - Jerarquía y permisos: solo el personal staff puede crear, listar
#     y eliminar colaboradores, mientras que un usuario normal solo puede
#     ver y editar su propio perfil
#   - Protección del superadmin: no se puede desactivar al último
#     superadmin activo del sistema ni un usuario puede darse de baja
#     a sí mismo
#   - Creación con perfil Collaborator, validación de unicidad de
#     username, email y documento, y generación automática de CUPE
#   - Listado con paginación, búsqueda y filtro por estado activo
#   - Edición de campos básicos, cambio de rol y manejo de duplicados
#   - Baja lógica que marca is_active=False sin eliminar el registro
#   - Endpoint /users/me para que el usuario autenticado vea su perfil
# =============================================================================

import pytest
from fastapi import status

try:
    from clients.models import Collaborator

    USERS_MODULE_READY = True
except ImportError:
    USERS_MODULE_READY = False

pytestmark = pytest.mark.skipif(
    not USERS_MODULE_READY,
    reason="El módulo users (Collaborator) no está disponible. Mergear feat/users-RF03 primero.",
)


# ---------------------------------------------------------------------------
# Fixtures compartidas para las pruebas de colaboradores
# ---------------------------------------------------------------------------

@pytest.fixture
def role_admin():
    """Crea un rol de tipo 'Admin' para asignar a usuarios con permisos de staff."""
    from clients.models import Role
    import uuid
    return Role.objects.create(
        id=uuid.uuid4(),
        name="Admin",
        description="Administrador del sistema",
    )


@pytest.fixture
def role_editor():
    """Crea un rol de tipo 'Editor' para asignar a usuarios sin permisos de staff."""
    from clients.models import Role
    import uuid
    return Role.objects.create(
        id=uuid.uuid4(),
        name="Editor",
        description="Editor de contenido",
    )


@pytest.fixture
def staff_user(role_admin):
    """Crea un usuario con permisos de staff que puede realizar operaciones administrativas como crear, listar y eliminar colaboradores."""
    from clients.models import User
    from django.contrib.auth.hashers import make_password
    import uuid
    return User.objects.create(
        id=uuid.uuid4(),
        username="staff",
        email="staff@example.com",
        password=make_password("staff123"),
        role=role_admin,
        is_active=True,
        is_staff=True,
    )


@pytest.fixture
def normal_user(role_editor):
    """Crea un usuario sin permisos de staff que solo puede ver y editar su propio perfil."""
    from clients.models import User
    from django.contrib.auth.hashers import make_password
    import uuid
    return User.objects.create(
        id=uuid.uuid4(),
        username="normal",
        email="normal@example.com",
        password=make_password("normal123"),
        role=role_editor,
        is_active=True,
        is_staff=False,
    )


@pytest.fixture
def super_admin_user():
    """Crea un superadmin con is_superuser=True para probar la protección que impide desactivar al último superadmin activo del sistema."""
    from clients.models import User
    from django.contrib.auth.hashers import make_password
    import uuid
    return User.objects.create(
        id=uuid.uuid4(),
        username="superadmin",
        email="super@example.com",
        password=make_password("super123"),
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def staff_token(staff_user):
    """Genera un token JWT de acceso para el usuario staff para autenticar las peticiones que requieren permisos administrativos."""
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(staff_user.id)})


@pytest.fixture
def normal_token(normal_user):
    """Genera un token JWT de acceso para un usuario normal sin permisos de staff."""
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(normal_user.id)})


@pytest.fixture
def super_token(super_admin_user):
    """Genera un token JWT de acceso para el superadmin para probar las restricciones de seguridad sobre este tipo de usuario."""
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(super_admin_user.id)})


@pytest.fixture
def staff_client(client, staff_token):
    """Configura un cliente HTTP con el token del usuario staff en el encabezado de autorización."""
    client.headers["Authorization"] = f"Bearer {staff_token}"
    return client


@pytest.fixture
def normal_client(client, normal_token):
    """Configura un cliente HTTP con el token de un usuario normal sin permisos de staff."""
    client.headers["Authorization"] = f"Bearer {normal_token}"
    return client


@pytest.fixture
def super_client(client, super_token):
    """Configura un cliente HTTP con el token del superadmin para probar las restricciones de seguridad."""
    client.headers["Authorization"] = f"Bearer {super_token}"
    return client


@pytest.fixture
def create_user_payload(role_editor):
    """Proporciona la carga útil estándar para crear un colaborador de prueba con todos los campos del formulario de registro."""
    return {
        "username": "nuevo_colaborador",
        "password": "Segura123!",
        "email": "nuevo@example.com",
        "first_name": "Nuevo",
        "last_name": "Colaborador",
        "role_id": str(role_editor.id),
        "document_number": "DOC123456",
        "phone": "555-1234",
        "area": "Ventas",
        "notes": "Colaborador de prueba",
    }


# ---------------------------------------------------------------------------
# JERARQUÍA Y PERMISOS
# Verifica que el sistema controle correctamente qué acciones puede
# realizar cada tipo de usuario según su rol y permisos asignados
# ---------------------------------------------------------------------------

class TestHierarchyAndPermissions:
    """
    Pruebas que validan la jerarquía de roles y los permisos del sistema:
    solo los usuarios con is_staff=True pueden realizar operaciones
    administrativas como crear, listar y eliminar colaboradores,
    mientras que los usuarios normales solo pueden ver y editar
    su propio perfil.
    """

    def test_staff_can_create_user(self, staff_client, create_user_payload):
        """Verifica que un usuario con permisos de staff pueda crear un nuevo colaborador en el sistema."""
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "nuevo_colaborador"
        assert data["is_active"] is True

    def test_normal_user_cannot_create_user(self, normal_client, create_user_payload):
        """Verifica que un usuario normal sin permisos de staff reciba un error 403 al intentar crear un colaborador."""
        response = normal_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_cannot_list_users(self, client):
        """Verifica que un cliente no autenticado reciba un error 403 al intentar listar los colaboradores del sistema."""
        response = client.get("/api/v1/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_list_users(self, staff_client):
        """Verifica que un usuario staff pueda obtener el listado completo de colaboradores registrados en el sistema."""
        response = staff_client.get("/api/v1/users")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1

    def test_normal_user_cannot_list_users(self, normal_client):
        """Verifica que un usuario normal reciba un error 403 al intentar listar todos los colaboradores del sistema."""
        response = normal_client.get("/api/v1/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_normal_user_can_see_own_profile(self, normal_client, normal_user):
        """Verifica que un usuario normal pueda ver su propio perfil consultando su ID."""
        response = normal_client.get(f"/api/v1/users/{normal_user.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "normal"

    def test_normal_user_cannot_see_other_profile(self, normal_client, staff_user):
        """Verifica que un usuario normal reciba un error 403 al intentar ver el perfil de otro colaborador."""
        response = normal_client.get(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_see_any_profile(self, staff_client, normal_user):
        """Verifica que un usuario staff pueda ver el perfil de cualquier colaborador del sistema."""
        response = staff_client.get(f"/api/v1/users/{normal_user.id}")
        assert response.status_code == status.HTTP_200_OK

    def test_normal_user_can_edit_own_profile(self, normal_client, normal_user):
        """Verifica que un usuario normal pueda editar su propio perfil, por ejemplo cambiando su nombre."""
        response = normal_client.put(
            f"/api/v1/users/{normal_user.id}",
            json={"first_name": "Editado"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Editado"

    def test_normal_user_cannot_edit_other_profile(self, normal_client, staff_user):
        """Verifica que un usuario normal reciba un error 403 al intentar editar el perfil de otro colaborador."""
        response = normal_client.put(
            f"/api/v1/users/{staff_user.id}",
            json={"first_name": "Hackeado"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# PROTECCIÓN DEL SUPERADMIN
# Reglas de seguridad que protegen la integridad del sistema evitando
# que se desactive al último superadmin o que un usuario se autoelimine
# ---------------------------------------------------------------------------

class TestSuperAdminProtection:
    """
    Pruebas que verifican las reglas de protección del superadmin:
    no se puede desactivar al único superadmin activo del sistema,
    no se puede desactivar a través de actualización, y un usuario
    normal no puede desactivar a un superadmin.
    También verifica que un usuario no pueda darse de baja a sí mismo.
    """

    def test_cannot_deactivate_last_superadmin(self, super_client, super_admin_user):
        """Verifica que el sistema rechace la desactivación del único superadmin activo con un error 400."""
        response = super_client.delete(f"/api/v1/users/{super_admin_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "superadmin" in response.json()["detail"].lower()

    def test_cannot_deactivate_last_superadmin_via_update(self, super_client, super_admin_user):
        """Verifica que tampoco se pueda desactivar al último superadmin mediante el endpoint de actualización con is_active=False."""
        response = super_client.put(
            f"/api/v1/users/{super_admin_user.id}",
            json={"is_active": False},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_staff_cannot_deactivate_superadmin(self, normal_client, super_admin_user):
        """Verifica que un usuario normal reciba un error 403 al intentar desactivar a un superadmin."""
        response = normal_client.delete(f"/api/v1/users/{super_admin_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_self_deactivate(self, staff_client, staff_user):
        """Verifica que un usuario no pueda darse de baja a sí mismo, recibiendo un error 400."""
        response = staff_client.delete(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ti mismo" in response.json()["detail"].lower()

    def test_only_staff_can_change_is_active(self, normal_client, normal_user):
        """Verifica que un usuario normal reciba un error 403 al intentar cambiar su propio estado is_active."""
        response = normal_client.put(
            f"/api/v1/users/{normal_user.id}",
            json={"is_active": False},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# CREACIÓN DE COLABORADORES
# Pruebas específicas del proceso de alta de colaboradores incluyendo
# la creación del perfil Collaborator y las validaciones de unicidad
# ---------------------------------------------------------------------------

class TestCreateUser:
    """
    Pruebas para la creación de colaboradores que verifican la correcta
    generación del perfil Collaborator, la unicidad de username y email,
    y la validación de campos obligatorios.
    """

    def test_create_user_creates_collaborator_profile(self, staff_client, create_user_payload):
        """Verifica que al crear un colaborador se genere automáticamente su perfil Collaborator con teléfono, área, documento y CUPE."""
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["phone"] == "555-1234"
        assert data["area"] == "Ventas"
        assert data["document_number"] == "DOC123456"
        assert data["cupe"].startswith("ELO-")

    def test_create_duplicate_username(self, staff_client, create_user_payload):
        """Verifica que el sistema rechace la creación de un colaborador con un nombre de usuario que ya está registrado."""
        staff_client.post("/api/v1/users", json=create_user_payload)
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "username" in response.json()["detail"].lower()

    def test_create_duplicate_email(self, staff_client, create_user_payload):
        """Verifica que el sistema rechace la creación de un colaborador con un correo electrónico que ya está registrado por otro usuario."""
        staff_client.post("/api/v1/users", json=create_user_payload)
        payload = create_user_payload.copy()
        payload["username"] = "otro_user"
        response = staff_client.post("/api/v1/users", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email" in response.json()["detail"].lower()

    def test_create_without_required_fields(self, staff_client):
        """Verifica que el sistema rechace la creación cuando no se proporcionan campos obligatorios como username y password."""
        response = staff_client.post("/api/v1/users", json={"username": "", "password": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# LISTADO Y FILTROS
# Pruebas para el listado de colaboradores con paginación, búsqueda
# por nombre de usuario y filtro por estado activo o inactivo
# ---------------------------------------------------------------------------

class TestListUsers:
    """
    Pruebas que verifican el correcto funcionamiento del listado de
    colaboradores incluyendo la paginación, la búsqueda por username
    y el filtrado por estado is_active.
    """

    def test_list_pagination(self, staff_client, create_user_payload):
        """Verifica que el listado devuelva la cantidad correcta de colaboradores después de crear dos registros."""
        staff_client.post("/api/v1/users", json=create_user_payload)
        payload2 = create_user_payload.copy()
        payload2["username"] = "otro_user"
        payload2["email"] = "otro@example.com"
        payload2["document_number"] = "DOC999999"
        staff_client.post("/api/v1/users", json=payload2)
        response = staff_client.get("/api/v1/users")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 2

    def test_list_search_by_username(self, staff_client, create_user_payload):
        """Verifica que la búsqueda por nombre de usuario filtre correctamente los resultados."""
        staff_client.post("/api/v1/users", json=create_user_payload)
        response = staff_client.get("/api/v1/users?search=nuevo_colaborador")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_list_filter_by_is_active(self, staff_client, create_user_payload):
        """Verifica que el filtro por is_active=true devuelva los colaboradores activos y el filtro is_active=false devuelva los inactivos después de una baja lógica."""
        created = staff_client.post("/api/v1/users", json=create_user_payload).json()
        staff_client.delete(f"/api/v1/users/{created['id']}")
        response = staff_client.get("/api/v1/users?is_active=true")
        assert response.status_code == status.HTTP_200_OK
        response_inactive = staff_client.get("/api/v1/users?is_active=false")
        assert response_inactive.status_code == status.HTTP_200_OK
        assert response_inactive.json()["count"] >= 1


# ---------------------------------------------------------------------------
# EDICIÓN DE COLABORADORES
# Pruebas que verifican la actualización de datos personales, cambio
# de rol, manejo de registros inexistentes y validación de unicidad
# ---------------------------------------------------------------------------

class TestUpdateUser:
    """
    Pruebas para el endpoint de actualización de colaboradores que
    verifican la modificación de campos básicos, el cambio de rol,
    el manejo de IDs inexistentes y la protección contra duplicados.
    """

    @pytest.fixture
    def created_user(self, staff_client, create_user_payload):
        """Crea un colaborador de prueba para ser utilizado en las pruebas de actualización."""
        return staff_client.post("/api/v1/users", json=create_user_payload).json()

    def test_update_basic_fields(self, staff_client, created_user):
        """Verifica que se pueda modificar el nombre y apellido de un colaborador existente."""
        response = staff_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"first_name": "Modificado", "last_name": "Apellido Nuevo"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Modificado"
        assert response.json()["last_name"] == "Apellido Nuevo"

    def test_update_role(self, staff_client, created_user, role_admin):
        """Verifica que se pueda cambiar el rol de un colaborador asignándole un rol diferente."""
        response = staff_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"role_id": str(role_admin.id)},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "Admin"

    def test_update_not_found(self, staff_client):
        """Verifica que el endpoint devuelva 404 cuando se intenta actualizar un colaborador que no existe en la base de datos."""
        response = staff_client.put(
            "/api/v1/users/00000000-0000-0000-0000-000000000000",
            json={"first_name": "Nadie"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_duplicate_username(self, staff_client, created_user, create_user_payload):
        """Verifica que el sistema rechace la actualización cuando se intenta asignar un nombre de usuario que ya está registrado por otro colaborador."""
        payload2 = create_user_payload.copy()
        payload2["username"] = "segundo_usuario"
        payload2["email"] = "segundo@example.com"
        payload2["document_number"] = "DOC999999"
        staff_client.post("/api/v1/users", json=payload2)
        response = staff_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"username": "segundo_usuario"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT


# ---------------------------------------------------------------------------
# BAJA LÓGICA
# Pruebas que verifican la desactivación de colaboradores marcándolos
# como inactivos sin eliminar el registro de la base de datos
# ---------------------------------------------------------------------------

class TestDeactivateUser:
    """
    Pruebas para la baja lógica de colaboradores que verifican la
    correcta desactivación, el manejo de IDs inexistentes y la
    restricción de que solo el staff pueda realizar esta operación.
    """

    @pytest.fixture
    def created_user(self, staff_client, create_user_payload):
        """Crea un colaborador de prueba para ser utilizado en las pruebas de baja lógica."""
        return staff_client.post("/api/v1/users", json=create_user_payload).json()

    def test_deactivate_user(self, staff_client, created_user):
        """Verifica que al dar de baja a un colaborador, este quede marcado como is_active=False pero su registro permanezca en la base de datos."""
        response = staff_client.delete(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        detail = staff_client.get(f"/api/v1/users/{created_user['id']}")
        assert detail.json()["is_active"] is False

    def test_deactivate_not_found(self, staff_client):
        """Verifica que el endpoint devuelva 404 cuando se intenta desactivar un colaborador que no existe."""
        response = staff_client.delete(
            "/api/v1/users/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_non_staff_cannot_deactivate(self, normal_client, staff_user):
        """Verifica que un usuario normal sin permisos de staff reciba un error 403 al intentar desactivar a otro colaborador."""
        response = normal_client.delete(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# ENDPOINT /users/me
# Pruebas que verifican que el endpoint de perfil propio devuelva
# los datos del usuario autenticado y rechace peticiones sin token
# ---------------------------------------------------------------------------

class TestMeEndpoint:
    """
    Pruebas para el endpoint /users/me que permite al usuario
    autenticado consultar su propio perfil completo incluyendo
    los datos del colaborador asociado.
    """

    def test_me_returns_authenticated_user(self, staff_client, staff_user):
        """Verifica que el endpoint /users/me devuelva los datos del usuario que realiza la petición autenticada."""
        response = staff_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == staff_user.username

    def test_me_without_auth(self, client):
        """Verifica que un cliente no autenticado reciba un error 403 al intentar acceder al endpoint /users/me."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
