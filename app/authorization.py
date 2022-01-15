from http import HTTPStatus

from fastapi import Header, HTTPException

from app.config import get_settings

settings = get_settings()


async def verify_key(x_api_key: str = Header("X-Api-Key")):
    if not x_api_key or x_api_key != settings.x_api_key:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Authorization information is invalid",
        )
