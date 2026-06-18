# =============================================================================
# Pruebas del Código Único de Persona ELISA (CUPE)
# Valida la generación automática y las reglas de unicidad:
#   - Generación automática con formato ELO-XXXXX al crear un colaborador
#   - Incremento secuencial: cada nuevo colaborador recibe el CUPE
#     siguiente al último generado
#   - Unicidad: cada colaborador debe tener un CUPE diferente
#   - Formato estandarizado de 9 caracteres con prefijo ELO- y
#     cinco dígitos numéricos con relleno de ceros
#   - Persistencia: el CUPE no debe cambiar al actualizar otros campos
#   - Disponibilidad en todas las respuestas: create, detail, list y me
# =============================================================================

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

# Expresión regular que valida el formato del CUPE: ELO- seguido de exactamente 5 dígitos numéricos
CUPE_PATTERN = re.compile(r"^ELO-\d{5}$")


# ---------------------------------------------------------------------------
# Fixtures compartidas para las pruebas de CUPE
# ---------------------------------------------------------------------------

@pytest.fixture
def staff_user():
    """Crea un usuario con permisos de staff para poder crear colaboradores a través de la API."""
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
    """Genera un token JWT de acceso para el usuario staff para autenticar las peticiones de creación de colaboradores."""
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(staff_user.id)})


@pytest.fixture
def staff_client(client, staff_token):
    """Configura un cliente HTTP con el token del usuario staff en el encabezado de autorización para las pruebas de CUPE."""
    client.headers["Authorization"] = f"Bearer {staff_token}"
    return client


@pytest.fixture
def user_payload():
    """Proporciona la carga útil estándar para crear un colaborador de prueba y verificar la generación de su CUPE."""
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
# Verifica que el sistema genere el CUPE automáticamente al crear
# un colaborador, que sea secuencial y que esté disponible en todas
# las respuestas del API
# ---------------------------------------------------------------------------

class TestCUPEGeneration:
    """
    Pruebas que verifican la generación automática del CUPE cuando
    se crea un nuevo colaborador a través del endpoint de usuarios.
    Valida que el formato sea correcto, que los números se incrementen
    secuencialmente y que el CUPE esté presente en las respuestas
    de creación, detalle, listado y perfil propio.
    """

    def test_cupe_generated_on_create(self, staff_client, user_payload):
        """Verifica que al crear un colaborador se genere automáticamente un CUPE que coincida con el patrón ELO-XXXXX."""
        response = staff_client.post("/api/v1/users", json=user_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["cupe"] != ""
        assert CUPE_PATTERN.match(data["cupe"]), f"CUPE '{data['cupe']}' no coincide con el patrón ELO-XXXXX"

    def test_cupe_increments_sequentially(self, staff_client, user_payload):
        """Verifica que los CUPE se generen secuencialmente: el segundo colaborador debe tener el número siguiente al primero."""
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
        """Verifica que el CUPE esté presente en las respuestas de detalle y listado además de la respuesta de creación."""
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
        """Verifica que el campo CUPE esté presente en la respuesta del endpoint de perfil propio del usuario autenticado."""
        created = staff_client.post("/api/v1/users", json=user_payload).json()
        me = staff_client.get("/api/v1/users/me")
        assert me.status_code == status.HTTP_200_OK
        assert "cupe" in me.json()

    def test_cupe_persists_after_update(self, staff_client, user_payload):
        """Verifica que el CUPE no cambie cuando se actualizan otros campos del colaborador como el nombre."""
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
# Verifica que cada colaborador tenga un CUPE único y diferente al
# de los demás colaboradores registrados en el sistema
# ---------------------------------------------------------------------------

class TestCUPEUniqueness:
    """
    Prueba que verifica la unicidad del CUPE: dos colaboradores
    distintos no pueden tener el mismo código CUPE asignado.
    """

    def test_cupe_is_unique(self, staff_client, user_payload):
        """Verifica que dos colaboradores diferentes reciban CUPE distintos y únicos en el sistema."""
        first = staff_client.post("/api/v1/users", json=user_payload).json()
        payload2 = user_payload.copy()
        payload2["username"] = "otro_cupe"
        payload2["email"] = "otro_cupe@example.com"
        payload2["document_number"] = "CUPE-DOC-003"
        second = staff_client.post("/api/v1/users", json=payload2).json()
        assert first["cupe"] != second["cupe"], "Dos colaboradores no pueden tener el mismo CUPE"


# ---------------------------------------------------------------------------
# FORMATO DEL CUPE
# Verifica que el CUPE cumpla con el formato estandarizado ELO-XXXXX
# donde ELO es el prefijo fijo y XXXXX son 5 dígitos numéricos
# ---------------------------------------------------------------------------

class TestCUPEFormat:
    """
    Pruebas que verifican el formato estandarizado del CUPE:
    debe comenzar con el prefijo 'ELO-', tener exactamente 9
    caracteres de longitud, y la parte numérica debe ser de 5
    dígitos con relleno de ceros a la izquierda.
    """

    def test_cupe_format_elomux(self, staff_client, user_payload):
        """Verifica que el CUPE comience con el prefijo ELO- y tenga exactamente 9 caracteres de longitud total."""
        response = staff_client.post("/api/v1/users", json=user_payload)
        cupe = response.json()["cupe"]
        assert cupe.startswith("ELO-"), f"CUPE debe empezar con ELO-, obtenido: {cupe}"
        assert len(cupe) == 9, f"CUPE debe tener 9 caracteres (ELO-XXXXX), obtenido: {cupe} (len={len(cupe)})"

    def test_cupe_zero_padded(self, staff_client, user_payload):
        """Verifica que la parte numérica del CUPE tenga exactamente 5 dígitos con relleno de ceros a la izquierda."""
        response = staff_client.post("/api/v1/users", json=user_payload)
        cupe = response.json()["cupe"]
        numero = cupe.replace("ELO-", "")
        assert numero.isdigit(), f"La parte numérica del CUPE debe ser dígitos: {numero}"
        assert len(numero) == 5, f"La parte numérica debe tener 5 dígitos: {numero}"
