"""Core application settings with Pydantic Settings."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Basketball Reference API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = "duckdb:///baller_hub.db"
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    meilisearch_url: str = "http://localhost:7700"
    meilisearch_api_key: str = ""

    scraper_base_url: str = "https://www.basketball-reference.com"
    scraper_rate_limit_seconds: float = 3.0

    jwt_secret_key: str = ""  # Required: set JWT_SECRET_KEY env var
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:3000"]

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    @model_validator(mode="after")
    def validate_required_settings(self) -> "Settings":
        if not self.jwt_secret_key or len(self.jwt_secret_key) < 32:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required and must be at least 32 characters"
            )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
