from http import HTTPStatus
from unittest.mock import MagicMock, patch

import redis
from fastapi.testclient import TestClient

from app.config import get_settings
from app.tests.test_consts import DB_GET_ENCRYPTED_VALUE, INVALID_X_API_KEY

settings = get_settings()


class TestGetParkingSlotStatus:
    def test_no_authorization(self, client: TestClient):
        response = client.get(
            "/get-parking-slot-status/",
            headers={"X-Api-Key": INVALID_X_API_KEY},
            params={"id": "123"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response_body["detail"] == "Authorization information is invalid"

    def test_invalid_data(self, client: TestClient):
        response = client.get(
            "/get-parking-slot-status/",
            headers={"X-Api-Key": settings.x_api_key},
            params={"hash": "123"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response_body["detail"] == [
            {
                "loc": ["query", "id"],
                "msg": "field required",
                "type": "value_error.missing",
            }
        ]

    @patch.object(redis.Redis, "get", return_value=DB_GET_ENCRYPTED_VALUE)
    def test_no_data_about_slot_given(self, redis_get_mock: MagicMock, client: TestClient):
        response = client.get(
            "/get-parking-slot-status/",
            headers={"X-Api-Key": settings.x_api_key},
            params={"id": "123456"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response_body["detail"] == "Parking slot with id 123456 not found"

    @patch.object(redis.Redis, "get", return_value=DB_GET_ENCRYPTED_VALUE)
    def test_parking_slot_state_known(self, redis_get_mock: MagicMock, client: TestClient):
        response = client.get(
            "/get-parking-slot-status/",
            headers={"X-Api-Key": settings.x_api_key},
            params={"id": "123"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.OK
        assert response_body == "free"
