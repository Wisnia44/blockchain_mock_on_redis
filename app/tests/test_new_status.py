import json
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import redis
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from app.config import get_settings
from app.models import ParkingSlot, ParkingSlotStatus, Transaction
from app.tests.test_consts import INVALID_X_API_KEY

settings = get_settings()
f = Fernet(settings.fernet_key_url_safe_base64_encoded)


class TestNewStatus:
    def test_no_authorization(self, client: TestClient):
        response = client.post(
            "/new-status/",
            headers={"X-Api-Key": INVALID_X_API_KEY},
            json={"id": "123", "status": "free"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response_body["detail"] == "Authorization information is invalid"

    def test_invalid_data(self, client: TestClient):
        response = client.post(
            "/new-status/",
            headers={"X-Api-Key": settings.x_api_key},
            json={"id": "123", "status": "bad_status"},
        )
        response_body = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response_body["detail"] == [
            {
                "ctx": {"enum_values": ["free", "locked", "maintenance", "occupied"]},
                "loc": ["body", "status"],
                "msg": "value is not a valid enumeration member; permitted: 'free', "
                "'locked', 'maintenance', 'occupied'",
                "type": "type_error.enum",
            }
        ]

    @patch.object(redis.Redis, "set")
    def test_valid_request(self, redis_set_mock: MagicMock, client: TestClient):
        response = client.post(
            "/new-status/",
            headers={"X-Api-Key": settings.x_api_key},
            json={"id": "123", "status": "free"},
        )
        assert response.status_code == HTTPStatus.OK
        real_call = redis_set_mock.call_args_list[0][1]
        real_hash = real_call["name"]
        real_value = real_call["value"]
        real_value_decrypted_dict = json.loads(f.decrypt(real_value))
        real_value_decrypted = Transaction(**real_value_decrypted_dict)
        expected_value = Transaction(
            hash=real_hash,
            previous_transaction="95d76e0e4a0a421d80996798a558f5c8",
            data=ParkingSlot(id="123", status=ParkingSlotStatus.FREE),
        )

        assert real_value_decrypted == expected_value
