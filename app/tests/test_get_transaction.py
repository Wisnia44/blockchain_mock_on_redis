from http import HTTPStatus
from unittest.mock import MagicMock, patch

import redis
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.config import get_settings
from app.tests.test_consts import DB_GET_ENCRYPTED_VALUE, INVALID_X_API_KEY

settings = get_settings()
f = Fernet(settings.fernet_key_url_safe_base64_encoded)


class TestGetTransaction:
    def test_no_authorization(self, client: TestClient):
        response = client.get(
            "/get-transaction/",
            headers={"X-Api-Key": INVALID_X_API_KEY},
            params={"hash": "95d76e0e4a0a421d80996798a558f5c8"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response_body["detail"] == "Authorization information is invalid"

    def test_invalid_data(self, client: TestClient):
        response = client.get(
            "/get-transaction/",
            headers={"X-Api-Key": settings.x_api_key},
            params={"id": "95d76e0e4a0a421d80996798a558f5c8"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response_body["detail"] == [
            {
                "loc": ["query", "hash"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]

    @patch.object(redis.Redis, "get", return_value=DB_GET_ENCRYPTED_VALUE)
    def test_valid_request(self, redis_get_mock: MagicMock, client: TestClient):
        response = client.get(
            "/get-transaction/",
            headers={"X-Api-Key": settings.x_api_key},
            params={"hash": "95d76e0e4a0a421d80996798a558f5c8"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.OK
        assert response_body["hash"] == "95d76e0e4a0a421d80996798a558f5c8"
        assert response_body["previous_transaction"] == "0"
        assert response_body["data"]["id"] == "123"
        assert response_body["data"]["status"] == "free"
        assert not response_body["data"]["occupied_by_car"]
