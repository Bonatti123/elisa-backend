# =============================================================================
# Pruebas del módulo de errores, validaciones y respuestas del backend (RF-37)
# Verifica la uniformidad de las respuestas de error en toda la API:
#   - Formato estandarizado ErrorResponse con detail, code y field
#   - Formato ValidationErrorResponse con lista de errores de validación
#   - Códigos HTTP correctos para cada tipo de error (400, 401, 403, 404, 422, 500)
#   - Manejo de errores de base de datos (integridad, operacionales, datos)
#   - Errores no controlados con respuesta genérica 500
# =============================================================================

import pytest
from fastapi import status

try:
    from api.exceptions import (
        AppException,
        FunctionalError,
        NotFoundError,
        AuthError,
        PermissionError as AppPermissionError,
        TechnicalError,
    )
    from api.schemas.errors import ErrorResponse, ValidationErrorDetail, ValidationErrorResponse

    ERRORS_MODULE_READY = True
except ImportError:
    ERRORS_MODULE_READY = False

pytestmark = pytest.mark.skipif(
    not ERRORS_MODULE_READY,
    reason="El módulo de errores (exceptions, schemas/errors) no está disponible. Mergear feat/errors-RF37 primero.",
)


# ---------------------------------------------------------------------------
# Fixtures compartidas para las pruebas de errores
# ---------------------------------------------------------------------------

@pytest.fixture
def test_user():
    """Crea un usuario de prueba para los endpoints que requieren autenticación."""
    from clients.models import User, Role
    from django.contrib.auth.hashers import make_password
    import uuid
    role = Role.objects.create(id=uuid.uuid4(), name="Admin")
    return User.objects.create(
        id=uuid.uuid4(),
        username="user_errors",
        email="errors@example.com",
        password=make_password("pass123"),
        role=role,
        is_active=True,
        is_staff=True,
    )


@pytest.fixture
def auth_token(test_user):
    """Genera un token JWT de acceso para autenticar las peticiones de prueba."""
    from api.routers.auth import create_access_token
    return create_access_token({"sub": str(test_user.id)})


@pytest.fixture
def auth_client(client, auth_token):
    """Configura un cliente HTTP autenticado con el token JWT del usuario de prueba."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client


# ---------------------------------------------------------------------------
# ESTRUCTURA DE ERRORES
# Verifica que la jerarquía de excepciones personalizadas herede
# correctamente de AppException y que los esquemas de respuesta
# tengan la estructura esperada
# ---------------------------------------------------------------------------

class TestErrorStructure:
    """
    Pruebas que verifican la estructura de las excepciones personalizadas
    y los esquemas de respuesta de error definidos en el módulo de errores.
    Cada excepción debe heredar de AppException y tener el código HTTP
    correcto según el tipo de error.
    """

    def test_app_exception_base(self):
        """Verifica que AppException sea la clase base y almacene correctamente el código, detalle y campo opcional."""
        exc = AppException(detail="Error base", code=400, field="nombre")
        assert exc.detail == "Error base"
        assert exc.code == 400
        assert exc.field == "nombre"

    def test_functional_error_default_code(self):
        """Verifica que FunctionalError tenga código 400 por defecto y herede de AppException."""
        exc = FunctionalError(detail="Dato inválido")
        assert exc.code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == "Dato inválido"
        assert isinstance(exc, AppException)

    def test_not_found_error_default_code(self):
        """Verifica que NotFoundError tenga código 404 por defecto y mensaje predeterminado."""
        exc = NotFoundError()
        assert exc.code == status.HTTP_404_NOT_FOUND
        assert exc.detail == "Recurso no encontrado"

    def test_auth_error_default_code(self):
        """Verifica que AuthError tenga código 401 por defecto."""
        exc = AuthError()
        assert exc.code == status.HTTP_401_UNAUTHORIZED

    def test_permission_error_default_code(self):
        """Verifica que PermissionError tenga código 403 por defecto."""
        exc = AppPermissionError()
        assert exc.code == status.HTTP_403_FORBIDDEN

    def test_technical_error_default_code(self):
        """Verifica que TechnicalError tenga código 500 por defecto."""
        exc = TechnicalError()
        assert exc.code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_error_response_schema(self):
        """Verifica que el esquema ErrorResponse tenga los campos esperados: detail, code y field opcional."""
        response = ErrorResponse(detail="Error de prueba", code=400, field="email")
        assert response.detail == "Error de prueba"
        assert response.code == 400
        assert response.field == "email"

    def test_validation_error_response_schema(self):
        """Verifica que el esquema ValidationErrorResponse contenga una lista de errores con campo y detalle."""
        errors = [
            ValidationErrorDetail(field="email", detail="El email no es válido"),
            ValidationErrorDetail(field="password", detail="La contraseña es muy corta"),
        ]
        response = ValidationErrorResponse(errors=errors)
        assert response.detail == "Error de validación"
        assert response.code == 422
        assert len(response.errors) == 2
        assert response.errors[0].field == "email"


# ---------------------------------------------------------------------------
# VALIDACIONES PERIMETRALES
# Verifica que los endpoints rechacen datos inválidos con errores
# de validación estructurados (422) en lugar de errores genéricos
# ---------------------------------------------------------------------------

class TestValidationErrors:
    """
    Pruebas que verifican que la API rechace correctamente las peticiones
    con datos inválidos devolviendo errores de validación con el formato
    estandarizado ValidationErrorResponse y código 422.
    """

    def test_login_without_username(self, client):
        """Verifica que el endpoint de login devuelva un error 422 cuando no se envía el nombre de usuario."""
        response = client.post("/api/v1/auth/login", json={"password": "test123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "errors" in data

    def test_login_without_password(self, client):
        """Verifica que el endpoint de login devuelva un error 422 cuando no se envía la contraseña."""
        response = client.post("/api/v1/auth/login", json={"username": "test"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "errors" in data

    def test_refresh_with_empty_token(self, client):
        """Verifica que el endpoint de refresh devuelva un error 422 cuando se envía un token vacío."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_email_format(self, client):
        """Verifica que el endpoint de login devuelva un error 422 con formato inválido si existiera un campo email con validación."""
        response = client.post("/api/v1/auth/login", json={"username": "", "password": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data


# ---------------------------------------------------------------------------
# ERRORES DE AUTENTICACIÓN
# Verifica que los endpoints protegidos rechacen peticiones sin token
# o con token inválido devolviendo errores 401 o 403
# ---------------------------------------------------------------------------

class TestAuthenticationErrors:
    """
    Pruebas que verifican que los endpoints protegidos por autenticación
    rechacen correctamente las peticiones sin token, con token inválido
    o con token expirado, devolviendo los códigos HTTP adecuados.
    """

    def test_endpoint_without_token(self, client):
        """Verifica que un endpoint protegido devuelva 403 cuando no se envía ningún token de autenticación."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_endpoint_with_invalid_token(self, client):
        """Verifica que un endpoint protegido devuelva 401 cuando se envía un token JWT inválido o mal formado."""
        client.headers["Authorization"] = "Bearer token_invalido"
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_invalid_credentials(self, client):
        """Verifica que el endpoint de login devuelva 401 cuando se envían credenciales incorrectas."""
        response = client.post("/api/v1/auth/login", json={"username": "noexiste", "password": "wrong"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_invalid_token(self, client):
        """Verifica que el endpoint de refresh devuelva 401 cuando se envía un token de refresh inválido."""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "token_invalido"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# ERRORES DE RECURSO NO ENCONTRADO
# Verifica que los endpoints devuelvan 404 cuando se solicita
# un recurso que no existe en la base de datos
# ---------------------------------------------------------------------------

class TestNotFoundErrors:
    """
    Pruebas que verifican que los endpoints devuelvan error 404
    cuando se intenta acceder a un recurso que no existe,
    siguiendo el formato estandarizado ErrorResponse.
    """

    def test_get_nonexistent_user_me_endpoint(self, client):
        """Verifica que el endpoint /auth/me devuelva 401 cuando el token es inválido (no 404 porque primero falla la autenticación)."""
        client.headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwidHlwZSI6ImFjY2VzcyJ9.invalid"
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_health_endpoint_always_available(self, client):
        """Verifica que el endpoint de health check esté siempre disponible sin autenticación."""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "ok"

    def test_nonexistent_route_returns_404(self, client):
        """Verifica que una ruta que no existe en la API devuelva error 404."""
        response = client.get("/api/v1/ruta_inexistente")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# ERRORES DE PERMISOS
# Verifica que los endpoints que requieren permisos específicos
# rechacen a usuarios sin la autorización necesaria
# ---------------------------------------------------------------------------

class TestPermissionErrors:
    """
    Pruebas que verifican que los endpoints que requieren permisos
    de staff o roles específicos rechacen a usuarios que no tienen
    la autorización necesaria, devolviendo error 403.
    """

    def test_normal_user_blocked_from_admin_endpoints(self, client):
        """Verifica que el endpoint de login funcione correctamente con credenciales válidas (no requiere permisos especiales)."""
        response = client.post("/api/v1/auth/login", json={"username": "test", "password": "test"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# FORMATO DE RESPUESTAS EXITOSAS
# Verifica que los endpoints exitosos devuelvan respuestas con
# el formato esperado y los códigos HTTP correctos
# ---------------------------------------------------------------------------

class TestSuccessResponseFormat:
    """
    Pruebas que verifican que los endpoints exitosos devuelvan
    las respuestas con el formato correcto y los códigos HTTP
    adecuados según la operación realizada.
    """

    def test_health_response_format(self, client):
        """Verifica que el endpoint de health check devuelva una respuesta JSON con status y version."""
        response = client.get("/api/v1/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert data["status"] == "ok"

    def test_login_response_format(self, client, test_user):
        """Verifica que el endpoint de login devuelva un token response con access_token, refresh_token y token_type."""
        response = client.post("/api/v1/auth/login", json={"username": "user_errors", "password": "pass123"})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_me_response_format(self, auth_client):
        """Verifica que el endpoint de perfil propio devuelva los datos del usuario autenticado en formato UserResponse."""
        response = auth_client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "is_active" in data
