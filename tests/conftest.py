import pytest
from fastapi.testclient import TestClient

from app.dependencies import store
from app.main import app


@pytest.fixture(autouse=True)
def _clean_store():
    store.clear()
    yield
    store.clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
