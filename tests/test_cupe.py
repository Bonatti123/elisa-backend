import re
import pytest
from fastapi import status

try:
    from clients.models import Collaborator

    CUPE_MODULE_READY = True
except ImportError:
    CUPE_MODULE_READY = False

pytestmark = pytest.mark.skipif(
    not CUPE_MODULE_READY,
    reason="El módulo users (Collaborator) no está disponible. Mergear feat/users-RF03 primero.",
)


CUPE_PATTERN = re.compile(r"^ELO-\d{5}$")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def staff_user():
    from clients.models import User, Role
    from django.contrib.auth.hashers import make_password
    import uuid
    role = Role.objects.create(id=uuid.uuid4(), name="Admin")
    user = User.objects.create(
        id=uuid.uuid4(),
        username="admin_cupe",
        email="admin@example.com",
        password=make_password("admin123"),
        role=role,
        is_active=True,
        is_staff=True,
    )
    return user


@pytest.fixture
def staff_token(staff_user):
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(staff_user.id)})


@pytest.fixture
def staff_client(client, staff_token):
    client.headers["Authorization"] = f"Bearer {staff_token}"
    return client


@pytest.fixture
def user_payload():
    return {
        "username": "colaborador_cupe",
        "password": "Pass123!",
        "email": "cupe@example.com",
        "first_name": "Test",
        "last_name": "CUPE",
        "document_number": "CUPE-DOC-001",
        "phone": "555-0001",
        "area": "IT",
    }


# ---------------------------------------------------------------------------
# GENERACIÓN AUTOMÁTICA DE CUPE
# ---------------------------------------------------------------------------

class TestCUPEGeneration:
    def test_cupe_generated_on_create(self, staff_client, user_payload):
        response = staff_client.post("/api/v1/users", json=user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["cupe"] != ""
        assert CUPE_PATTERN.match(data["cupe"]), f"CUPE '{data['cupe']}' no coincide con el patrón ELO-XXXXX"

    def test_cupe_increments_sequentially(self, staff_client, user_payload):
        first = staff_client.post("/api/v1/users", json=user_payload).json()
        payload2 = user_payload.copy()
        payload2["username"] = "colaborador2"
        payload2["email"] = "cupe2@example.com"
        payload2["document_number"] = "CUPE-DOC-002"
        second = staff_client.post("/api/v1/users", json=payload2).json()
        num1 = int(first["cupe"].replace("ELO-", ""))
        num2 = int(second["cupe"].replace("ELO-", ""))
        assert num2 == num1 + 1, f"CUPE debe ser secuencial: {first['cupe']} -> {second['cupe']}"

    def test_cupe_always_returns_in_user_response(self, staff_client, user_payload):
        created = staff_client.post("/api/v1/users", json=user_payload).json()
        detail = staff_client.get(f"/api/v1/users/{created['id']}")
        assert detail.status_code == status.HTTP_200_OK
        assert CUPE_PATTERN.match(detail.json()["cupe"])

        listing = staff_client.get("/api/v1/users")
        assert listing.status_code == status.HTTP_200_OK
        for u in listing.json()["results"]:
            if u["id"] == created["id"]:
                assert CUPE_PATTERN.match(u["cupe"])
                break
        else:
            pytest.fail("Usuario creado no encontrado en el listado")

    def test_cupe_on_me_endpoint(self, staff_client, user_payload):
        created = staff_client.post("/api/v1/users", json=user_payload).json()
        me = staff_client.get("/api/v1/users/me")
        assert me.status_code == status.HTTP_200_OK
        assert "cupe" in me.json()

    def test_cupe_persists_after_update(self, staff_client, user_payload):
        created = staff_client.post("/api/v1/users", json=user_payload).json()
        cupe_original = created["cupe"]
        response = staff_client.put(
            f"/api/v1/users/{created['id']}",
            json={"first_name": "Actualizado"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["cupe"] == cupe_original


# ---------------------------------------------------------------------------
# UNICIDAD DEL CUPE
# ---------------------------------------------------------------------------

class TestCUPEUniqueness:
    def test_cupe_is_unique(self, staff_client, user_payload):
        first = staff_client.post("/api/v1/users", json=user_payload).json()
        payload2 = user_payload.copy()
        payload2["username"] = "otro_cupe"
        payload2["email"] = "otro_cupe@example.com"
        payload2["document_number"] = "CUPE-DOC-003"
        second = staff_client.post("/api/v1/users", json=payload2).json()
        assert first["cupe"] != second["cupe"], "Dos colaboradores no pueden tener el mismo CUPE"


# ---------------------------------------------------------------------------
# FORMATO DEL CUPE
# ---------------------------------------------------------------------------

class TestCUPEFormat:
    def test_cupe_format_elomux(self, staff_client, user_payload):
        response = staff_client.post("/api/v1/users", json=user_payload)
        cupe = response.json()["cupe"]
        assert cupe.startswith("ELO-"), f"CUPE debe empezar con ELO-, obtenido: {cupe}"
        assert len(cupe) == 9, f"CUPE debe tener 9 caracteres (ELO-XXXXX), obtenido: {cupe} (len={len(cupe)})"

    def test_cupe_zero_padded(self, staff_client, user_payload):
        response = staff_client.post("/api/v1/users", json=user_payload)
        cupe = response.json()["cupe"]
        numero = cupe.replace("ELO-", "")
        assert numero.isdigit(), f"La parte numérica del CUPE debe ser dígitos: {numero}"
        assert len(numero) == 5, f"La parte numérica debe tener 5 dígitos: {numero}"
