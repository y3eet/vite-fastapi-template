from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str | None = "DEV"

    FRONTEND_URL: str | None = "http://localhost:5173"
    DATABASE_URL: str
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
