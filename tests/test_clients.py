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
    import uuid
    return WebFeature.objects.create(
        id=uuid.uuid4(),
        name="Chat Online",
        extra_price=Decimal("15.00"),
        is_active=True,
    )


@pytest.fixture
def client_payload(web_type):
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
# ALTAS (Create)
# ---------------------------------------------------------------------------

class TestCreateClient:
    def test_create_client_success(self, auth_client, client_payload):
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
        response = client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_client_duplicate_document(self, auth_client, client_payload):
        auth_client.post("/api/v1/clients/", json=client_payload)
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "documento" in response.json()["detail"].lower()

    def test_create_client_duplicate_email(self, auth_client, client_payload):
        auth_client.post("/api/v1/clients/", json=client_payload)
        payload = client_payload.copy()
        payload["document_number"] = "20987654321"
        response = auth_client.post("/api/v1/clients/", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "correo" in response.json()["detail"].lower()

    def test_create_client_with_features(self, auth_client, client_payload, web_feature):
        client_payload["feature_ids"] = [str(web_feature.id)]
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert Decimal(data["extra_price"]) == Decimal("15.00")
        assert Decimal(data["total_price"]) == Decimal("114.99")

    def test_create_client_plan_venta(self, auth_client, client_payload, web_type):
        client_payload["plan"] = "venta"
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert Decimal(data["base_price"]) == Decimal("499.99")

    def test_create_client_invalid_document_type(self, auth_client, client_payload):
        client_payload["document_type"] = "INVALIDO"
        response = auth_client.post("/api/v1/clients/", json=client_payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---------------------------------------------------------------------------
# LISTADO (Read / List)
# ---------------------------------------------------------------------------

class TestListClients:
    @pytest.fixture(autouse=True)
    def _create_clients(self, auth_client, client_payload):
        auth_client.post("/api/v1/clients/", json=client_payload)
        p2 = client_payload.copy()
        p2["document_number"] = "20987654321"
        p2["email"] = "otro@example.com"
        p2["name"] = "Otro Cliente"
        auth_client.post("/api/v1/clients/", json=p2)

    def test_list_default_pagination(self, auth_client):
        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["page_size"] == 20
        assert len(data["results"]) == 2

    def test_list_search_by_name(self, auth_client):
        response = auth_client.get("/api/v1/clients/?search=Cliente+Test")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["results"][0]["name"] == "Cliente Test"

    def test_list_search_by_document(self, auth_client):
        response = auth_client.get("/api/v1/clients/?search=20987654321")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

    def test_list_without_auth(self, client):
        response = client.get("/api/v1/clients/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# DETALLE (Read / Detail)
# ---------------------------------------------------------------------------

class TestGetClient:
    def test_get_client_success(self, auth_client, client_payload):
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        response = auth_client.get(f"/api/v1/clients/{created['id']}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created["id"]

    def test_get_client_not_found(self, auth_client):
        response = auth_client.get("/api/v1/clients/00000000-0000-0000-0000-000000000000")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_client_without_auth(self, client, auth_client, client_payload):
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        response = client.get(f"/api/v1/clients/{created['id']}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# EDICIÓN (Update)
# ---------------------------------------------------------------------------

class TestUpdateClient:
    @pytest.fixture
    def created_client(self, auth_client, client_payload):
        return auth_client.post("/api/v1/clients/", json=client_payload).json()

    def test_update_name_and_email(self, auth_client, created_client):
        response = auth_client.put(
            f"/api/v1/clients/{created_client['id']}",
            json={"name": "Cliente Modificado", "email": "modificado@example.com"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Cliente Modificado"
        assert data["email"] == "modificado@example.com"

    def test_update_delivery_date_activates_client(self, auth_client, created_client):
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
        response = auth_client.put(
            "/api/v1/clients/00000000-0000-0000-0000-000000000000",
            json={"name": "Nadie"},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_without_auth(self, client, created_client):
        response = client.put(
            f"/api/v1/clients/{created_client['id']}",
            json={"name": "Hackeado"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# BAJA LÓGICA (Delete)
# ---------------------------------------------------------------------------

class TestDeleteClient:
    @pytest.fixture
    def created_client(self, auth_client, client_payload):
        return auth_client.post("/api/v1/clients/", json=client_payload).json()

    def test_soft_delete(self, auth_client, created_client):
        response = auth_client.delete(f"/api/v1/clients/{created_client['id']}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        detail = auth_client.get(f"/api/v1/clients/{created_client['id']}")
        assert detail.status_code == status.HTTP_200_OK
        data = detail.json()
        assert data["is_active"] is False
        assert data["status"] == "inactivo"

    def test_delete_not_found(self, auth_client):
        response = auth_client.delete(
            "/api/v1/clients/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_without_auth(self, client, created_client):
        response = client.delete(f"/api/v1/clients/{created_client['id']}")
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# REGLAS DE NEGOCIO
# ---------------------------------------------------------------------------

class TestBusinessRules:
    def test_total_price_equals_base_plus_extra(self, auth_client, client_payload, web_feature):
        client_payload["feature_ids"] = [str(web_feature.id)]
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        base = Decimal(created["base_price"])
        extra = Decimal(created["extra_price"])
        total = Decimal(created["total_price"])
        assert total == base + extra

    def test_update_web_type_recalculates_prices(self, auth_client, client_payload):
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
        created = auth_client.post("/api/v1/clients/", json=client_payload).json()
        auth_client.put(f"/api/v1/clients/{created['id']}", json={"name": "Nuevo Nombre"})
        history = auth_client.get(f"/api/v1/clients/{created['id']}/history")
        assert history.status_code == status.HTTP_200_OK
        entries = history.json()
        assert len(entries) == 2
        actions = [e["accion"] for e in entries]
        assert "creacion" in actions
        assert "actualizacion" in actions
