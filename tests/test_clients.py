# =============================================================================
# Pruebas del módulo de gestión de clientes (RF-01)
# Valida el ciclo de vida completo del cliente:
#   - Alta con validaciones de unicidad y precios automáticos
#   - Listado con paginación, búsqueda y filtros
#   - Detalle de un cliente por su identificador único
#   - Edición con recálculo de precios y fechas
#   - Baja lógica que mantiene el registro histórico
#   - Reglas de negocio como precio total y auditoría
# =============================================================================

from decimal import Decimal
from datetime import date, timedelta

import pytest
from fastapi import status


try:
    from clients.models import Client, WebType, WebFeature

    CLIENTS_MODULE_READY = True
except ImportError:
    CLIENTS_MODULE_READY = False

pytestmark = pytest.mark.skipif(
    not CLIENTS_MODULE_READY,
    reason="El módulo clients (Client, WebType, WebFeature) no está disponible en esta rama. Mergear feat/clients-RF01 primero.",
)


@pytest.fixture
def web_type():
    """
    Crea un tipo de web 'Básica' con precios de alquiler y venta.
    Se utiliza como referencia para calcular el precio base del cliente
    según el plan que haya contratado.
    """
    import uuid
    return WebType.objects.create(
        id=uuid.uuid4(),
        name="Basica",
        base_price_rent=Decimal("99.99"),
        base_price_sale=Decimal("499.99"),
        is_active=True,
    )


@pytest.fixture
def web_feature(web_type):
    """
    Crea una funcionalidad extra 'Chat Online' con un precio adicional.
    Se utiliza para verificar que el precio total se calcule correctamente
    sumando el precio base más el precio de las funcionalidades extra.
    """
    import uuid
    return WebFeature.objects.create(
        id=uuid.uuid4(),
        name="Chat Online",
        extra_price=Decimal("15.00"),
        is_active=True,
    )


@pytest.fixture
def client_payload(web_type):
    """
    Proporciona la carga útil estándar para crear un cliente de prueba.
    Incluye todos los campos obligatorios y asigna el tipo de web creado
    anteriormente para que el cálculo de precios funcione correctamente.
    """
    return {
        "name": "Cliente Test",
        "document_type": "RUC",
        "document_number": "20123456789",
        "email": "cliente@example.com",
        "phone": "999888777",
        "plan": "alquiler",
        "status": "en_desarrollo",
        "payment_frequency": "mensual",
        "web_type_id": str(web_type.id),
        "feature_ids": [],
        "notes": "Cliente de prueba",
    }


# ---------------------------------------------------------------------------
# ALTAS
# ---------------------------------------------------------------------------

class TestCreateClient:
    """
    Pruebas para el endpoint de creación de clientes.
    Verifica que se creen correctamente con todos los campos,
    que se rechacen documentos y correos duplicados,
    que las funcionalidades extra se agreguen correctamente,
    que el plan afecte el precio base y que los tipos de documento
    inválidos sean rechazados por el validador de esquemas.
    """

    def test_create_client_success(self, auth_client, client_payload):
        """Crea un cliente con datos válidos y verifica que la respuesta contenga todos los campos esperados incluyendo CUPE, precios y creador."""
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Cliente Test"
        assert data["document_number"] == "20123456789"
        assert data["email"] == "cliente@example.com"
        assert data["plan"] == "alquiler"
        assert data["status"] == "en_desarrollo"
        assert data["is_active"] is True
        assert data["cupe"].startswith("ELO")
        assert Decimal(data["base_price"]) == Decimal("99.99")
        assert Decimal(data["total_price"]) == Decimal("99.99")
        assert data["created_by"] == "testuser"

    def test_create_client_without_auth(self, client, client_payload):
        """Verifica que un cliente no autenticado reciba un error 403 al intentar crear un cliente."""
        response = client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_client_duplicate_document(self, auth_client, client_payload):
        """Verifica que el sistema rechace la creación de un cliente con un número de documento que ya está registrado en otro cliente."""
        auth_client.post("/api/v1/clients/", json=client_payload)
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "documento" in response.json()["detail"].lower()

    def test_create_client_duplicate_email(self, auth_client, client_payload):
        """Verifica que el sistema rechace la creación de un cliente con un correo electrónico que ya está registrado por otro cliente."""
        auth_client.post("/api/v1/clients/", json=client_payload)
        payload = client_payload.copy()
        payload["document_number"] = "20987654321"
        response = auth_client.post("/api/v1/clients/", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "correo" in response.json()["detail"].lower()

    def test_create_client_with_features(self, auth_client, client_payload, web_feature):
        """Verifica que al crear un cliente con funcionalidades extra, el precio adicional se sume correctamente al precio total."""
        client_payload["feature_ids"] = [str(web_feature.id)]
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert Decimal(data["extra_price"]) == Decimal("15.00")
        assert Decimal(data["total_price"]) == Decimal("114.99")

    def test_create_client_plan_venta(self, auth_client, client_payload, web_type):
        """Verifica que al crear un cliente con plan de venta, el precio base sea el precio de venta del tipo de web en lugar del de alquiler."""
        client_payload["plan"] = "venta"
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert Decimal(data["base_price"]) == Decimal("499.99")

    def test_create_client_invalid_document_type(self, auth_client, client_payload):
        """Verifica que el sistema rechace la creación con un tipo de documento que no esté en la lista de valores permitidos."""
        client_payload["document_type"] = "INVALIDO"
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# LISTADO
# ---------------------------------------------------------------------------

class TestListClients:
    """
    Pruebas para el endpoint de listado de clientes.
    Verifica la paginación por defecto, la búsqueda por nombre y documento,
    y que los usuarios no autenticados no puedan acceder al listado.
    """

    @pytest.fixture(autouse=True)
    def _create_clients(self, auth_client, client_payload):
        """Crea dos clientes de prueba antes de cada prueba de listado para tener datos que verificar."""
        auth_client.post("/api/v1/clients/", json=client_payload)
        p2 = client_payload.copy()
        p2["document_number"] = "20987654321"
        p2["email"] = "otro@example.com"
        p2["name"] = "Otro Cliente"
        auth_client.post("/api/v1/clients/", json=p2)

    def test_list_default_pagination(self, auth_client):
        """Verifica que el listado devuelva los dos clientes creados con la paginación predeterminada de 20 resultados por página."""
        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["results"]) == 2

    def test_list_search_by_name(self, auth_client):
        """Verifica que la búsqueda por nombre filtre correctamente y devuelva solo el cliente cuyo nombre coincide."""
        response = auth_client.get("/api/v1/clients/?search=Cliente+Test")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["results"][0]["name"] == "Cliente Test"

    def test_list_search_by_document(self, auth_client):
        """Verifica que la búsqueda por número de documento devuelva el cliente que tenga ese documento registrado."""
        response = auth_client.get("/api/v1/clients/?search=20987654321")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

    def test_list_without_auth(self, client):
        """Verifica que un cliente no autenticado reciba un error 403 al intentar listar los clientes del sistema."""
        response = client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# DETALLE
# ---------------------------------------------------------------------------

class TestGetClient:
    """
    Pruebas para el endpoint de detalle de un cliente.
    Verifica que se pueda obtener un cliente por su ID,
    que devuelva 404 si no existe y que rechace peticiones no autenticadas.
    """

    def test_get_client_success(self, auth_client, client_payload):
        """Crea un cliente y luego lo obtiene por su ID para verificar que los datos coincidan con los de la creación."""
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        response = auth_client.get(f"/api/v1/clients/{created['id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created["id"]

    def test_get_client_not_found(self, auth_client):
        """Verifica que el endpoint devuelva 404 cuando se solicita un cliente con un ID que no existe en la base de datos."""
        response = auth_client.get("/api/v1/clients/00000000-0000-0000-0000-000000000000")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_client_without_auth(self, client, auth_client, client_payload):
        """Verifica que un usuario no autenticado no pueda obtener el detalle de un cliente existente."""
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        response = client.get(f"/api/v1/clients/{created['id']}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# EDICIÓN
# ---------------------------------------------------------------------------

class TestUpdateClient:
    """
    Pruebas para el endpoint de actualización de clientes.
    Verifica la modificación de campos básicos, el cambio de estado
    al asignar fecha de entrega, el manejo de clientes inexistentes
    y la protección contra peticiones no autenticadas.
    """

    @pytest.fixture
    def created_client(self, auth_client, client_payload):
        """Crea un cliente de prueba para ser utilizado en las pruebas de actualización."""
        return auth_client.post("/api/v1/clients/", json=client_payload).json()

    def test_update_name_and_email(self, auth_client, created_client):
        """Verifica que se pueda modificar el nombre y el correo electrónico de un cliente existente."""
        response = auth_client.put(
            f"/api/v1/clients/{created_client['id']}",
            json={"name": "Cliente Modificado", "email": "modificado@example.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Cliente Modificado"
        assert data["email"] == "modificado@example.com"

    def test_update_delivery_date_activates_client(self, auth_client, created_client):
        """Verifica que al asignar una fecha de entrega, el cliente pase automáticamente a estado activo y se calcule su próxima fecha de pago."""
        delivery = date.today() + timedelta(days=1)
        response = auth_client.put(
            f"/api/v1/clients/{created_client['id']}",
            json={"delivery_date": delivery.isoformat()},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "activo"
        assert data["next_payment_date"] is not None

    def test_update_not_found(self, auth_client):
        """Verifica que el endpoint devuelva 404 cuando se intenta actualizar un cliente que no existe."""
        response = auth_client.put(
            "/api/v1/clients/00000000-0000-0000-0000-000000000000",
            json={"name": "Nadie"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_without_auth(self, client, created_client):
        """Verifica que un usuario no autenticado reciba un error 403 al intentar modificar un cliente existente."""
        response = client.put(
            f"/api/v1/clients/{created_client['id']}",
            json={"name": "Hackeado"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# BAJA LÓGICA
# ---------------------------------------------------------------------------

class TestDeleteClient:
    """
    Pruebas para el endpoint de eliminación lógica de clientes.
    Verifica que al eliminar un cliente se marque como inactivo,
    que su estado cambie a inactivo, que maneje IDs inexistentes
    y que rechace peticiones no autenticadas.
    """

    @pytest.fixture
    def created_client(self, auth_client, client_payload):
        """Crea un cliente de prueba para ser utilizado en las pruebas de eliminación lógica."""
        return auth_client.post("/api/v1/clients/", json=client_payload).json()

    def test_soft_delete(self, auth_client, created_client):
        """Verifica que al eliminar un cliente, este quede marcado como inactivo y su estado cambie a inactivo, pero su registro permanezca en la base de datos."""
        response = auth_client.delete(f"/api/v1/clients/{created_client['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        detail = auth_client.get(f"/api/v1/clients/{created_client['id']}")
        assert detail.status_code == status.HTTP_200_OK
        data = detail.json()
        assert data["is_active"] is False
        assert data["status"] == "inactivo"

    def test_delete_not_found(self, auth_client):
        """Verifica que el endpoint devuelva 404 cuando se intenta eliminar un cliente que no existe en la base de datos."""
        response = auth_client.delete(
            "/api/v1/clients/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_without_auth(self, client, created_client):
        """Verifica que un usuario no autenticado reciba un error 403 al intentar eliminar un cliente existente."""
        response = client.delete(f"/api/v1/clients/{created_client['id']}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# REGLAS DE NEGOCIO
# ---------------------------------------------------------------------------

class TestBusinessRules:
    """
    Pruebas que validan las reglas de negocio del módulo de clientes:
    - El precio total debe ser la suma del precio base más los extras
    - Al cambiar el tipo de web, el precio base debe recalcularse
    - Las operaciones de creación y actualización deben quedar registradas
      en el historial de auditoría del cliente
    """

    def test_total_price_equals_base_plus_extra(self, auth_client, client_payload, web_feature):
        """Verifica la regla de negocio que establece que el precio total del cliente debe ser exactamente la suma del precio base más el precio de las funcionalidades extra contratadas."""
        client_payload["feature_ids"] = [str(web_feature.id)]
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        base = Decimal(created["base_price"])
        extra = Decimal(created["extra_price"])
        total = Decimal(created["total_price"])
        assert total == base + extra

    def test_update_web_type_recalculates_prices(self, auth_client, client_payload):
        """Verifica que al cambiar el tipo de web de un cliente, el precio base se recalcule automáticamente según el nuevo tipo de web seleccionado."""
        import uuid

        otro_tipo = WebType.objects.create(
            id=uuid.uuid4(),
            name="Premium",
            base_price_rent=Decimal("199.99"),
            base_price_sale=Decimal("999.99"),
            is_active=True,
        )
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        assert Decimal(created["base_price"]) == Decimal("99.99")

        response = auth_client.put(
            f"/api/v1/clients/{created['id']}",
            json={"web_type_id": str(otro_tipo.id)},
        )
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.json()["base_price"]) == Decimal("199.99")

    def test_history_endpoint(self, auth_client, client_payload):
        """Verifica que cada operación de creación y actualización sobre un cliente quede registrada en el historial de auditoría del endpoint correspondiente."""
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        auth_client.put(f"/api/v1/clients/{created['id']}", json={"name": "Nuevo Nombre"})
        history = auth_client.get(f"/api/v1/clients/{created['id']}/history")
        assert history.status_code == status.HTTP_200_OK
        entries = history.json()
        assert len(entries) == 2
        actions = [e["accion"] for e in entries]
        assert "creacion" in actions
        assert "actualizacion" in actions
