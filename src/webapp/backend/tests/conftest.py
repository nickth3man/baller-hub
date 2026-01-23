"""Shared test fixtures for the backend test suite."""

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app.

    The TestClient does not call the lifespan events by default,
    which prevents database initialization during tests.
    """
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def client_with_lifespan():
    """Create a TestClient that triggers lifespan events.

    Use this fixture when you need database access.
    """
    with TestClient(app) as c:
        yield c
