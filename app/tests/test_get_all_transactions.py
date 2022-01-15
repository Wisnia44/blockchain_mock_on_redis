from http import HTTPStatus
from unittest.mock import MagicMock, patch

import redis
from fastapi.testclient import TestClient

from app.config import get_settings
from app.tests.test_consts import DB_GET_ENCRYPTED_VALUE, INVALID_X_API_KEY

settings = get_settings()


class TestGetAllTransactions:
    def test_no_authorization(self, client: TestClient):
        response = client.get(
            "/get-all-transactions/",
            headers={"X-Api-Key": INVALID_X_API_KEY},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response_body["detail"] == "Authorization information is invalid"

    @patch.object(redis.Redis, "get", return_value=DB_GET_ENCRYPTED_VALUE)
    def test_valid_request(self, redis_get_mock: MagicMock, client: TestClient):
        response = client.get(
            "/get-all-transactions/",
            headers={"X-Api-Key": settings.x_api_key},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.OK
        assert response_body[0]["hash"] == "95d76e0e4a0a421d80996798a558f5c8"
        assert response_body[0]["previous_transaction"] == "0"
        assert response_body[0]["data"]["id"] == "123"
        assert response_body[0]["data"]["status"] == "free"
        assert not response_body[0]["data"]["occupied_by_car"]
