import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

settings = get_settings()


@pytest.fixture(autouse=True)
def client(app=app):
    test_client = TestClient(app)
    return test_client
