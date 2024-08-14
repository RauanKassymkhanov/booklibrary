from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        case_sensitive=True,
        frozen=True,
        env_file=".env",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
