import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

settings = get_settings()
app.last_transaction_hash = "95d76e0e4a0a421d80996798a558f5c8"


@pytest.fixture(autouse=True)
def client(app=app):
    test_client = TestClient(app)
    return test_client
