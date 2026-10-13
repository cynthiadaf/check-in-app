"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API."""

    app_name: str = "Guest Check-In Manager"
    database_url: str = "postgresql+asyncpg://checkin:checkin@localhost:5432/checkin"
    cors_origins: str = "http://localhost:3000"
    timezone: str = "UTC"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()

