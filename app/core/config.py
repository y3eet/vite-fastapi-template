from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str | None = "DEV"

    FRONTEND_URL: str | None = "http://localhost:5173"
    DATABASE_URL: str
    DEBUG: bool = False

    COOKIE_DOMAIN: str = "localhost"
    JWT_ACCESS_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
