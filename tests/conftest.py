# =============================================================================
# Configuración global de pruebas para el sistema ELISA
# Proporciona las fixtures compartidas por todos los módulos de prueba:
#   - Base de datos SQLite en memoria para pruebas aisladas
#   - Cliente HTTP autenticado y no autenticado para probar endpoints
#   - Usuario y rol base para los casos de prueba
# =============================================================================

import os
import uuid

import django
from django.contrib.auth.hashers import make_password
from fastapi.testclient import TestClient

# Configurar Django antes de importar cualquier modelo o app
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Forzar el uso de SQLite para las pruebas, evitando depender de PostgreSQL
os.environ["DB_ENGINE"] = "sqlite3"

django.setup()

from django.conf import settings
from django.db import connections

# Usar base de datos en memoria para que cada ejecución de pruebas sea rápida y aislada
settings.DATABASES["default"]["NAME"] = ":memory:"

from api.main import app
from api.routers.auth import get_current_user
from clients.models import Role, User

import pytest


@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Crea todas las tablas de la base de datos antes de cada prueba
    y las elimina después para garantizar un estado limpio.
    Esto permite que cada prueba ejecute con una base de datos fresca.
    """
    with connections["default"].schema_editor() as schema_editor:
        for model in django.apps.apps.get_models():
            try:
                schema_editor.create_model(model)
            except Exception:
                pass
    yield
    with connections["default"].schema_editor() as schema_editor:
        for model in reversed(django.apps.apps.get_models()):
            try:
                schema_editor.delete_model(model)
            except Exception:
                pass


@pytest.fixture
def test_role():
    """
    Crea un rol de tipo 'Admin' que se utiliza como referencia
    para los usuarios creados durante las pruebas.
    """
    role, _ = Role.objects.get_or_create(
        name="Admin",
        defaults={"description": "Rol administrador para pruebas"},
    )
    return role


@pytest.fixture
def test_user(test_role):
    """
    Crea un usuario de prueba con permisos de staff (is_staff=True)
    para poder acceder a los endpoints que requieren autenticación
    y autorización de personal administrativo.
    """
    user = User.objects.create(
        id=uuid.uuid4(),
        username="testuser",
        email="test@example.com",
        password=make_password("testpass123"),
        role=test_role,
        is_active=True,
        is_staff=True,
    )
    return user


@pytest.fixture
def auth_token(test_user):
    """
    Genera un token JWT de tipo 'access' para el usuario de prueba.
    Este token se coloca en el encabezado Authorization de las
    peticiones HTTP para simular un usuario autenticado.
    """
    from api.routers.auth import create_access_token

    token = create_access_token({"sub": str(test_user.id)})
    return token


@pytest.fixture
def client():
    """
    Proporciona un cliente HTTP de prueba sin autenticación.
    Se utiliza para verificar que los endpoints rechacen
    correctamente las peticiones no autorizadas.
    """
    return TestClient(app)


@pytest.fixture
def auth_client(client, auth_token):
    """
    Proporciona un cliente HTTP de prueba con el token JWT
    ya configurado en el encabezado Authorization.
    Se utiliza para probar los endpoints que requieren
    autenticación de personal administrativo (staff).
    """
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
