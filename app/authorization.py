from http import HTTPStatus
from typing import Optional

from fastapi import Request, status
from fastapi.security.api_key import APIKeyHeader

from app.config import get_settings

settings = get_settings()


class XApiHeaderAuth(APIKeyHeader):
    def __init__(self):
        super().__init__(name="X-API-Key", auto_error=False)

    async def __call__(self, request: Request) -> Optional[str]:
        x_api_key = await super().__call__(request)

        if not x_api_key or x_api_key != settings.x_api_key:
            raise Exception(
                status_code=HTTPStatus.UNAUTHORIZED.value,
                content={"content": "Authorization information is invalid"},
            )

        return x_api_key
