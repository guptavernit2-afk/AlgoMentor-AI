"""
AlgoMentor AI — database connection layer.

Uses SQLAlchemy 2.x with psycopg 3 (psycopg:// dialect) to connect to
Supabase PostgreSQL through the Session Pooler.

Key design decisions
--------------------
- The engine is created lazily (only when get_engine() is called), so importing
  this module at startup never causes a connection attempt or a credential error.
- The database URL is assembled using SQLAlchemy's URL.create() rather than
  string concatenation.  This safely percent-encodes any special characters
  (!, @, # …) that Supabase may include in a generated password.
- The raw password is extracted from pydantic's SecretStr only at the last
  moment, inside _build_db_url(), and is never stored in a plain variable or
  included in application logs.
- ssl_require is passed as a connect_arg rather than baked into the URL so that
  it works correctly with psycopg 3's keyword-argument interface.

Public API
----------
    get_engine()                 → SQLAlchemy Engine (cached singleton)
    check_database_connection()  → dict {"status": "connected", "database": "…"}
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.engine import URL

if TYPE_CHECKING:
    from sqlalchemy import Engine

from app.config import get_settings


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_db_url() -> URL:
    """
    Construct a SQLAlchemy URL from the current settings.

    Uses URL.create() so that any special characters in the password are
    percent-encoded automatically — no manual escaping required.

    Raises RuntimeError (not ValueError) if required fields are absent, so
    the caller gets a clear message without SQLAlchemy swallowing context.
    """
    settings = get_settings()

    try:
        settings.validate_postgres_fields()
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    # get_secret_value() returns the plain string — used only here, never stored.
    password = settings.db_password.get_secret_value()  # type: ignore[union-attr]

    return URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=password,       # URL.create percent-encodes this safely
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def get_engine() -> "Engine":
    """
    Build and return the SQLAlchemy Engine singleton.

    The engine is created lazily on first call.  Subsequent calls return the
    cached instance.  Call `get_engine.cache_clear()` in tests that need a
    fresh engine.

    SSL is enforced via connect_args rather than the URL so that psycopg 3
    handles it correctly on all platforms.
    """
    settings = get_settings()
    url = _build_db_url()

    connect_args: dict = {}
    if settings.db_sslmode == "require":
        connect_args["sslmode"] = "require"

    return sa.create_engine(
        url,
        connect_args=connect_args,
        # Keep the pool small during the connection-foundation phase.
        pool_size=2,
        max_overflow=3,
        pool_pre_ping=True,   # detect stale connections before handing them out
        pool_recycle=300,     # recycle connections every 5 minutes (Supabase pooler)
        echo=False,           # set True temporarily for SQL debug logging
    )


# ---------------------------------------------------------------------------
# Connection health check
# ---------------------------------------------------------------------------

def check_database_connection() -> dict:
    """
    Execute a trivial `SELECT 1` to verify the connection is alive.

    Returns:
        {"status": "connected", "database": "<db_name>"}

    Raises:
        RuntimeError  if configuration is missing or the connection fails.
                      The error message is safe to print — it never contains
                      the password or the full connection URL.
    """
    settings = get_settings()

    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": settings.db_name,
        }
    except RuntimeError:
        # Re-raise config errors (missing fields) as-is — already safe.
        raise
    except Exception as exc:
        # Wrap low-level driver errors; strip any URL/password that might
        # appear in the original exception message.
        raise RuntimeError(
            f"Database connection failed: {type(exc).__name__} — "
            "check DB_HOST, DB_USER, DB_PASSWORD and DB_SSLMODE in backend/.env."
        ) from None
