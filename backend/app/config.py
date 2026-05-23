"""
AlgoMentor AI — application settings.

Loads configuration from backend/.env (if present) using pydantic-settings.
All database credentials are handled as SecretStr so they are never printed
in tracebacks, logs, or repr output.

Usage:
    from app.config import get_settings
    settings = get_settings()
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application-wide settings loaded from environment / .env file.

    Field naming follows the environment variable names exactly so that
    pydantic-settings maps them without any alias configuration.
    """

    # ------------------------------------------------------------------
    # Storage backend selector
    # ------------------------------------------------------------------
    # "memory"   → use the current in-memory dictionaries (default, safe).
    # "postgres" → connect to Supabase PostgreSQL via the Session Pooler.
    storage_backend: Literal["memory", "postgres"] = "memory"

    # ------------------------------------------------------------------
    # PostgreSQL / Supabase Session Pooler connection fields
    # ------------------------------------------------------------------
    # These are optional so the app starts without a .env file.
    # They are validated as a group only when storage_backend == "postgres".
    db_host: str | None = None
    db_port: int = 5432
    db_name: str = "postgres"
    db_user: str | None = None
    db_password: SecretStr | None = None
    db_sslmode: str = "require"

    # ------------------------------------------------------------------
    # Frontend origin fields (CORS)
    # ------------------------------------------------------------------
    frontend_origin: str = "http://localhost:5173"
    frontend_origin_alt: str = "http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Ignore extra env vars that are not declared above.
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Validation helper
    # ------------------------------------------------------------------

    def validate_postgres_fields(self) -> None:
        """
        Raise ValueError if any required field is missing when
        storage_backend is set to "postgres".

        Call this before attempting a database connection rather than
        at startup so that "memory" mode never fails due to missing DB vars.
        """
        if self.storage_backend != "postgres":
            return

        missing: list[str] = []
        if not self.db_host:
            missing.append("DB_HOST")
        if not self.db_user:
            missing.append("DB_USER")
        if not self.db_password:
            missing.append("DB_PASSWORD")

        if missing:
            raise ValueError(
                "STORAGE_BACKEND is set to 'postgres' but the following "
                f"required environment variables are not set: {', '.join(missing)}. "
                "Copy backend/.env.example to backend/.env and fill in the values."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    The cache means .env is read exactly once per process lifetime.
    Call `get_settings.cache_clear()` in tests that need to override env vars.
    """
    return Settings()
