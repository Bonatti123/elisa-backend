import os
import uuid
from unittest.mock import patch

import django
from django.contrib.auth.hashers import make_password
from fastapi.testclient import TestClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

os.environ["DB_ENGINE"] = "sqlite3"

django.setup()

from django.conf import settings
from django.db import connections

settings.DATABASES["default"]["NAME"] = ":memory:"

from api.main import app
from api.routers.auth import get_current_user
from clients.models import Role, User

import pytest


@pytest.fixture(autouse=True)
def setup_test_db():
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
    role, _ = Role.objects.get_or_create(
        name="Admin",
        defaults={"description": "Admin role for tests"},
    )
    return role


@pytest.fixture
def test_user(test_role):
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
    from api.routers.auth import create_access_token

    token = create_access_token({"sub": str(test_user.id)})
    return token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_client(client, auth_token):
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
