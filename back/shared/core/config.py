"""
Application configuration using Pydantic Settings.

This module defines all application configuration with environment variable
support, validation, and type safety.
"""

from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with validation."""

    model_config = SettingsConfigDict(
        env_file=".env.production",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Scan", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(..., description="Secret key for JWT/sessions")

    # Database
    database_url: PostgresDsn = Field(
        ..., description="PostgreSQL connection URL (asyncpg)"
    )
    db_pool_size: int = Field(default=20, ge=5, le=100, description="Database pool size")
    db_max_overflow: int = Field(
        default=10, ge=0, le=50, description="Database max overflow"
    )

    # Redis
    redis_url: RedisDsn = Field(..., description="Redis connection URL")

    # Security
    cors_origins: list[str] = Field(
        default=["http://localhost:4200"],
        description="Allowed CORS origins",
    )
    access_token_expire_minutes: int = Field(
        default=30, ge=5, le=1440, description="Access token expiration (minutes)"
    )

    # External Services (Optional)
    smtp_host: str | None = Field(default=None, description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: str | None = Field(default=None, description="SMTP username")
    smtp_password: str | None = Field(default=None, description="SMTP password")

    # Workers
    worker_concurrency: int = Field(
        default=4, ge=1, le=16, description="Worker concurrency level"
    )

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug


settings = Settings()
