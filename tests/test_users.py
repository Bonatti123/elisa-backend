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
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def role_admin():
    from clients.models import Role
    import uuid
    return Role.objects.create(
        id=uuid.uuid4(),
        name="Admin",
        description="Administrador del sistema",
    )


@pytest.fixture
def role_editor():
    from clients.models import Role
    import uuid
    return Role.objects.create(
        id=uuid.uuid4(),
        name="Editor",
        description="Editor de contenido",
    )


@pytest.fixture
def staff_user(role_admin):
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
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(staff_user.id)})


@pytest.fixture
def normal_token(normal_user):
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(normal_user.id)})


@pytest.fixture
def super_token(super_admin_user):
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(super_admin_user.id)})


@pytest.fixture
def staff_client(client, staff_token):
    client.headers["Authorization"] = f"Bearer {staff_token}"
    return client


@pytest.fixture
def normal_client(client, normal_token):
    client.headers["Authorization"] = f"Bearer {normal_token}"
    return client


@pytest.fixture
def super_client(client, super_token):
    client.headers["Authorization"] = f"Bearer {super_token}"
    return client


@pytest.fixture
def create_user_payload(role_editor):
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
# ---------------------------------------------------------------------------

class TestHierarchyAndPermissions:
    def test_staff_can_create_user(self, staff_client, create_user_payload):
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "nuevo_colaborador"
        assert data["is_active"] is True

    def test_normal_user_cannot_create_user(self, normal_client, create_user_payload):
        response = normal_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthorized_cannot_list_users(self, client):
        response = client.get("/api/v1/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_list_users(self, staff_client):
        response = staff_client.get("/api/v1/users")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] >= 1

    def test_normal_user_cannot_list_users(self, normal_client):
        response = normal_client.get("/api/v1/users")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_normal_user_can_see_own_profile(self, normal_client, normal_user):
        response = normal_client.get(f"/api/v1/users/{normal_user.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "normal"

    def test_normal_user_cannot_see_other_profile(self, normal_client, staff_user):
        response = normal_client.get(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_see_any_profile(self, staff_client, normal_user):
        response = staff_client.get(f"/api/v1/users/{normal_user.id}")
        assert response.status_code == status.HTTP_200_OK

    def test_normal_user_can_edit_own_profile(self, normal_client, normal_user):
        response = normal_client.put(
            f"/api/v1/users/{normal_user.id}",
            json={"first_name": "Editado"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Editado"

    def test_normal_user_cannot_edit_other_profile(self, normal_client, staff_user):
        response = normal_client.put(
            f"/api/v1/users/{staff_user.id}",
            json={"first_name": "Hackeado"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# PROTECCIÓN DEL SUPERADMIN
# ---------------------------------------------------------------------------

class TestSuperAdminProtection:
    def test_cannot_deactivate_last_superadmin(self, super_client, super_admin_user):
        response = super_client.delete(f"/api/v1/users/{super_admin_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "superadmin" in response.json()["detail"].lower()

    def test_cannot_deactivate_last_superadmin_via_update(self, super_client, super_admin_user):
        response = super_client.put(
            f"/api/v1/users/{super_admin_user.id}",
            json={"is_active": False},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_staff_cannot_deactivate_superadmin(self, normal_client, super_admin_user):
        response = normal_client.delete(f"/api/v1/users/{super_admin_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_self_deactivate(self, staff_client, staff_user):
        response = staff_client.delete(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ti mismo" in response.json()["detail"].lower()

    def test_only_staff_can_change_is_active(self, normal_client, normal_user):
        response = normal_client.put(
            f"/api/v1/users/{normal_user.id}",
            json={"is_active": False},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# CREACIÓN DE COLABORADORES
# ---------------------------------------------------------------------------

class TestCreateUser:
    def test_create_user_creates_collaborator_profile(self, staff_client, create_user_payload):
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["phone"] == "555-1234"
        assert data["area"] == "Ventas"
        assert data["document_number"] == "DOC123456"
        assert data["cupe"].startswith("ELO-")

    def test_create_duplicate_username(self, staff_client, create_user_payload):
        staff_client.post("/api/v1/users", json=create_user_payload)
        response = staff_client.post("/api/v1/users", json=create_user_payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "username" in response.json()["detail"].lower()

    def test_create_duplicate_email(self, staff_client, create_user_payload):
        staff_client.post("/api/v1/users", json=create_user_payload)
        payload = create_user_payload.copy()
        payload["username"] = "otro_user"
        response = staff_client.post("/api/v1/users", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email" in response.json()["detail"].lower()

    def test_create_without_required_fields(self, staff_client):
        response = staff_client.post("/api/v1/users", json={"username": "", "password": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# LISTADO Y FILTROS
# ---------------------------------------------------------------------------

class TestListUsers:
    def test_list_pagination(self, staff_client, create_user_payload):
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
        staff_client.post("/api/v1/users", json=create_user_payload)
        response = staff_client.get("/api/v1/users?search=nuevo_colaborador")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 1

    def test_list_filter_by_is_active(self, staff_client, create_user_payload):
        created = staff_client.post("/api/v1/users", json=create_user_payload).json()
        staff_client.delete(f"/api/v1/users/{created['id']}")
        response = staff_client.get("/api/v1/users?is_active=true")
        assert response.status_code == status.HTTP_200_OK
        response_inactive = staff_client.get("/api/v1/users?is_active=false")
        assert response_inactive.status_code == status.HTTP_200_OK
        assert response_inactive.json()["count"] >= 1


# ---------------------------------------------------------------------------
# EDICIÓN DE COLABORADORES
# ---------------------------------------------------------------------------

class TestUpdateUser:
    @pytest.fixture
    def created_user(self, staff_client, create_user_payload):
        return staff_client.post("/api/v1/users", json=create_user_payload).json()

    def test_update_basic_fields(self, staff_client, created_user):
        response = staff_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"first_name": "Modificado", "last_name": "Apellido Nuevo"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["first_name"] == "Modificado"
        assert response.json()["last_name"] == "Apellido Nuevo"

    def test_update_role(self, staff_client, created_user, role_admin):
        response = staff_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"role_id": str(role_admin.id)},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["role"] == "Admin"

    def test_update_not_found(self, staff_client):
        response = staff_client.put(
            "/api/v1/users/00000000-0000-0000-0000-000000000000",
            json={"first_name": "Nadie"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_duplicate_username(self, staff_client, created_user, create_user_payload):
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
# ---------------------------------------------------------------------------

class TestDeactivateUser:
    @pytest.fixture
    def created_user(self, staff_client, create_user_payload):
        return staff_client.post("/api/v1/users", json=create_user_payload).json()

    def test_deactivate_user(self, staff_client, created_user):
        response = staff_client.delete(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        detail = staff_client.get(f"/api/v1/users/{created_user['id']}")
        assert detail.json()["is_active"] is False

    def test_deactivate_not_found(self, staff_client):
        response = staff_client.delete(
            "/api/v1/users/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_non_staff_cannot_deactivate(self, normal_client, staff_user):
        response = normal_client.delete(f"/api/v1/users/{staff_user.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# ENDPOINT /users/me
# ---------------------------------------------------------------------------

class TestMeEndpoint:
    def test_me_returns_authenticated_user(self, staff_client, staff_user):
        response = staff_client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["username"] == staff_user.username

    def test_me_without_auth(self, client):
        response = client.get("/api/v1/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN
