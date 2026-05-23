"""
AlgoMentor AI — tests for app/config.py and app/database.py.

These tests NEVER connect to the real Supabase database.
They verify:
  - Default storage backend is "memory".
  - Postgres mode fails fast when required fields are absent.
  - URL construction handles special characters in the password correctly.
  - SecretStr prevents the password from appearing in repr/str output.
  - Existing API tests are unaffected (stores still use memory backend).

Run from backend/:
    pytest tests/test_database_config.py -v
"""

import pytest
from unittest.mock import patch, MagicMock
from pydantic import SecretStr
from sqlalchemy.engine import URL


# ============================================================
# Helpers
# ============================================================

def _make_settings(**overrides):
    """
    Build a Settings object with fully controlled field values,
    bypassing .env file loading entirely.

    Uses model_construct() which skips pydantic validation and env-file
    reading — perfect for unit tests that control every field explicitly.
    """
    from app.config import Settings

    defaults = dict(
        storage_backend="memory",
        db_host=None,
        db_port=5432,
        db_name="postgres",
        db_user=None,
        db_password=None,
        db_sslmode="require",
    )
    defaults.update(overrides)
    return Settings.model_construct(**defaults)


# ============================================================
# A. Default storage backend
# ============================================================

def test_default_storage_backend_is_memory():
    """When no env is supplied, storage_backend must default to 'memory'."""
    from app.config import Settings

    # Patch os.environ to be empty and point env_file at a non-existent path.
    with patch.dict("os.environ", {}, clear=True):
        s = Settings(_env_file="nonexistent_path.env")  # type: ignore[call-arg]
        assert s.storage_backend == "memory"


def test_default_db_fields_are_none_or_defaults():
    """Database fields default to None (host/user/password) when no env is set."""
    from app.config import Settings

    with patch.dict("os.environ", {}, clear=True):
        s = Settings(_env_file="nonexistent_path.env")  # type: ignore[call-arg]
        assert s.db_host is None
        assert s.db_user is None
        assert s.db_password is None
        assert s.db_port == 5432
        assert s.db_name == "postgres"
        assert s.db_sslmode == "require"


# ============================================================
# B. Postgres mode requires host/user/password
# ============================================================

def test_validate_postgres_fields_passes_when_all_set():
    """No exception when all required fields are present."""
    s = _make_settings(
        storage_backend="postgres",
        db_host="db.supabase.example.com",
        db_user="postgres.abc123",
        db_password=SecretStr("s3cr3t"),
    )
    s.validate_postgres_fields()  # must not raise


def test_validate_postgres_fields_raises_when_host_missing():
    s = _make_settings(
        storage_backend="postgres",
        db_host=None,
        db_user="postgres.abc123",
        db_password=SecretStr("s3cr3t"),
    )
    with pytest.raises(ValueError, match="DB_HOST"):
        s.validate_postgres_fields()


def test_validate_postgres_fields_raises_when_user_missing():
    s = _make_settings(
        storage_backend="postgres",
        db_host="db.supabase.example.com",
        db_user=None,
        db_password=SecretStr("s3cr3t"),
    )
    with pytest.raises(ValueError, match="DB_USER"):
        s.validate_postgres_fields()


def test_validate_postgres_fields_raises_when_password_missing():
    s = _make_settings(
        storage_backend="postgres",
        db_host="db.supabase.example.com",
        db_user="postgres.abc123",
        db_password=None,
    )
    with pytest.raises(ValueError, match="DB_PASSWORD"):
        s.validate_postgres_fields()


def test_validate_postgres_fields_is_noop_for_memory_backend():
    """Memory backend must pass even when all DB fields are absent."""
    s = _make_settings(storage_backend="memory")
    s.validate_postgres_fields()  # must not raise


def test_validate_postgres_fields_error_lists_all_missing():
    """When multiple fields are missing, all are listed in the error message."""
    s = _make_settings(
        storage_backend="postgres",
        db_host=None,
        db_user=None,
        db_password=None,
    )
    with pytest.raises(ValueError) as exc_info:
        s.validate_postgres_fields()
    msg = str(exc_info.value)
    assert "DB_HOST" in msg
    assert "DB_USER" in msg
    assert "DB_PASSWORD" in msg


# ============================================================
# C. URL construction safely handles special characters
# ============================================================

def test_url_create_encodes_special_chars_in_password():
    """
    SQLAlchemy URL.create() must percent-encode passwords containing
    characters that would break a naive URL string: !, @, #, $, %, &, +, =
    """
    nasty_password = "p@$$w0rd!&#special="

    url = URL.create(
        drivername="postgresql+psycopg",
        username="postgres.abc123",
        password=nasty_password,
        host="db.example.com",
        port=5432,
        database="postgres",
    )

    rendered = url.render_as_string(hide_password=False)

    # There must be exactly one '@' separating credentials from host.
    # The password's '@' signs must have been percent-encoded.
    assert rendered.count("@") == 1
    assert "db.example.com" in rendered


def test_url_create_hides_password_in_repr():
    """URL.render_as_string(hide_password=True) must redact the password."""
    url = URL.create(
        drivername="postgresql+psycopg",
        username="user",
        password="s3cr3t!",
        host="db.example.com",
        port=5432,
        database="postgres",
    )
    safe_repr = url.render_as_string(hide_password=True)
    assert "s3cr3t" not in safe_repr
    assert "***" in safe_repr


def test_secret_str_password_not_leaked_in_repr():
    """pydantic SecretStr must not expose the password in repr or str."""
    secret = SecretStr("my-very-secret-password!")
    assert "my-very-secret-password" not in repr(secret)
    assert "my-very-secret-password" not in str(secret)
    # But get_secret_value() must return it.
    assert secret.get_secret_value() == "my-very-secret-password!"


# ============================================================
# D. get_engine raises RuntimeError (not a raw driver error) when config missing
# ============================================================

def test_get_engine_raises_runtime_error_when_fields_missing():
    """
    Calling get_engine() in postgres mode without DB credentials must raise
    a RuntimeError with a safe, informative message — not a raw SQLAlchemy error.
    """
    from app import database as db_module
    from app import config as cfg_module

    # Clear caches so the patch takes effect.
    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()

    incomplete = _make_settings(
        storage_backend="postgres",
        db_host=None,
        db_user=None,
        db_password=None,
    )

    with patch("app.database.get_settings", return_value=incomplete):
        with pytest.raises(RuntimeError) as exc_info:
            db_module.get_engine()

    msg = str(exc_info.value)
    # Message must name the missing variables and be safe to display.
    assert "DB_HOST" in msg or "required" in msg.lower() or "not set" in msg.lower()

    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()


# ============================================================
# E. check_database_connection in memory mode fails without network call
# ============================================================

def test_check_database_connection_raises_in_memory_mode():
    """
    In memory mode validate_postgres_fields() raises ValueError which
    database.py wraps into RuntimeError — no network call is ever made.
    """
    from app import database as db_module
    from app import config as cfg_module

    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()

    memory_settings = _make_settings(storage_backend="memory")

    with patch("app.database.get_settings", return_value=memory_settings):
        with pytest.raises(RuntimeError):
            db_module.check_database_connection()

    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()


def test_check_database_connection_returns_dict_on_success():
    """
    When the engine connects successfully, check_database_connection()
    returns {"status": "connected", "database": "<db_name>"}.
    The engine is mocked — no real network call is made.
    """
    from app import database as db_module
    from app import config as cfg_module

    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()

    postgres_settings = _make_settings(
        storage_backend="postgres",
        db_host="db.example.com",
        db_user="postgres.abc123",
        db_password=SecretStr("s3cr3t"),
        db_name="postgres",
    )

    # Mock the engine and its context manager so no real connection is attempted.
    mock_conn = MagicMock()
    mock_engine = MagicMock()
    mock_engine.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
    mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)

    with patch("app.database.get_settings", return_value=postgres_settings):
        with patch("app.database.get_engine", return_value=mock_engine):
            result = db_module.check_database_connection()

    assert result["status"] == "connected"
    assert result["database"] == "postgres"
    mock_conn.execute.assert_called_once()

    db_module.get_engine.cache_clear()
    cfg_module.get_settings.cache_clear()
