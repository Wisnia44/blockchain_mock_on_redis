import base64
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    fernet_key: str = "30f98e425b6142e3b2bdeaf00224f459"

    @property
    def fernet_key_url_safe_base64_encoded(self):
        return base64.urlsafe_b64encode(self.fernet_key.encode("utf-8"))

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
