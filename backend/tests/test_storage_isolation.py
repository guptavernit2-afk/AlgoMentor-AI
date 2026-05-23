"""
AlgoMentor AI — Storage isolation tests.

Proves that the standard pytest suite is completely isolated from
live Supabase even when backend/.env contains STORAGE_BACKEND=postgres.

Five explicit isolation guarantees are verified here:

  1. The profile API lifecycle during pytest always uses MemoryProfileRepository.
  2. PUT /api/users/test-user/profile does not invoke a PostgreSQL engine.
  3. GET /api/users/test-user/profile reads from memory after PUT.
  4. The Postgres repository can still be constructed without a live connection.
  5. The database access guard raises AssertionError if a live engine is attempted.

These tests complement the three-layer isolation implemented in conftest.py.

Run from backend/:
    pytest tests/test_storage_isolation.py -v
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app


# ============================================================
# Shared fixtures / data
# (conftest autouse fixtures already clear caches + stores per test)
# ============================================================

VALID_PROFILE = {
    "name": "IsolationTest",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ============================================================
# 1. Profile lifecycle uses MemoryProfileRepository during pytest
# ============================================================

def test_profile_api_uses_memory_repository_during_pytest():
    """
    get_profile_repository() must return a MemoryProfileRepository even
    when STORAGE_BACKEND=postgres is written in backend/.env.

    conftest.py forces os.environ["STORAGE_BACKEND"] = "memory" at module
    import time before any app code runs, so pydantic-settings reads
    "memory" from the environment (higher priority than .env file).
    """
    from app.repositories.profile_repository import (
        get_profile_repository,
        MemoryProfileRepository,
    )

    repo = get_profile_repository()
    assert isinstance(repo, MemoryProfileRepository), (
        f"Expected MemoryProfileRepository but got {type(repo).__name__}. "
        "Tests are running against the live database — check conftest.py."
    )


def test_storage_backend_env_var_is_memory_during_pytest():
    """
    os.environ["STORAGE_BACKEND"] must be "memory" inside pytest.
    This confirms conftest.py's Layer 1 has taken effect.
    """
    assert os.environ.get("STORAGE_BACKEND") == "memory", (
        "STORAGE_BACKEND is not 'memory' inside pytest. "
        "conftest.py Layer 1 override is not working."
    )


def test_settings_reads_memory_backend_during_pytest():
    """
    get_settings().storage_backend must be "memory" inside pytest,
    regardless of what backend/.env contains.
    """
    from app.config import get_settings
    settings = get_settings()
    assert settings.storage_backend == "memory", (
        f"settings.storage_backend = {settings.storage_backend!r} but expected 'memory'. "
        "The .env file is overriding os.environ — check conftest.py Layer 1."
    )


# ============================================================
# 2. PUT profile does not invoke the PostgreSQL engine
# ============================================================

def test_put_profile_does_not_call_db_engine(client):
    """
    PUT /api/users/test-user/profile must complete successfully without
    calling PostgresProfileRepository._engine().

    The conftest _block_live_db_engine fixture replaces _engine() with a
    guard that raises AssertionError. If this test passes, no DB call was made.
    """
    r = client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    assert r.status_code == 200
    # If we reach here, _engine() was never called (no AssertionError)


# ============================================================
# 3. GET profile reads from memory after PUT
# ============================================================

def test_get_profile_reads_from_memory_after_put(client):
    """
    After a PUT, GET must return the same data — proving data stayed in
    memory and was not lost in a network roundtrip to Supabase.
    """
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    r = client.get("/api/users/test-user/profile")
    assert r.status_code == 200
    data = r.json()
    assert data["profile"]["name"] == "IsolationTest"
    assert data["profile"]["current_topic"] == "Hashing"


def test_get_profile_returns_404_for_unknown_user(client):
    """
    Without a prior PUT, GET must return 404 — confirming tests start
    with an empty in-memory store (conftest clears stores per test).
    """
    r = client.get("/api/users/isolation-ghost/profile")
    assert r.status_code == 404


# ============================================================
# 4. Postgres repository can be constructed without a live connection
# ============================================================

def test_postgres_repo_construction_does_not_open_connection():
    """
    Constructing a PostgresProfileRepository must not open any DB connection.
    The engine is lazy — it is only created when save_profile/get_profile
    calls _engine().  Mere construction must always be safe.
    """
    from app.repositories.profile_repository import PostgresProfileRepository

    # If this raises, construction is not safe (regression).
    repo = PostgresProfileRepository()
    assert repo is not None


def test_factory_selects_postgres_repo_without_connecting():
    """
    When storage_backend is forced to 'postgres' via patched settings,
    the factory returns a PostgresProfileRepository without opening a
    connection.  The conftest guard on _engine() proves no connection
    was attempted (if it were, AssertionError would propagate here).
    """
    from app.repositories.profile_repository import (
        get_profile_repository,
        PostgresProfileRepository,
    )
    from app.config import Settings

    postgres_settings = Settings.model_construct(
        storage_backend="postgres",
        db_host="db.example.com",
        db_user="user",
        db_password=None,
        db_name="postgres",
        db_port=5432,
        db_sslmode="require",
    )

    with patch("app.config.get_settings", return_value=postgres_settings):
        get_profile_repository.cache_clear()
        repo = get_profile_repository()  # must NOT raise or connect

    assert isinstance(repo, PostgresProfileRepository)
    get_profile_repository.cache_clear()


# ============================================================
# 5. Database access guard fires if _engine() is called directly
# ============================================================

def test_db_guard_raises_assertion_error_if_engine_called():
    """
    Directly calling PostgresProfileRepository._engine() during pytest must
    raise an AssertionError because conftest's _block_live_db_engine fixture
    has replaced it with a forbidden-engine guard.

    This confirms Layer 3 of the isolation strategy is active.
    """
    from app.repositories.profile_repository import PostgresProfileRepository

    repo = PostgresProfileRepository()
    with pytest.raises(AssertionError, match="forbidden during pytest"):
        repo._engine()


def test_db_guard_prevents_save_profile_from_connecting():
    """
    Attempting to call save_profile() on PostgresProfileRepository must
    fail before any network I/O can occur.

    The conftest guard replaces _engine() with a function that raises
    AssertionError.  save_profile() catches all non-RuntimeError exceptions
    and wraps them in a RuntimeError — so the caller sees a RuntimeError
    whose message contains "AssertionError", proving the guard fired.
    """
    from app.models import StudentProfile
    from app.repositories.profile_repository import PostgresProfileRepository

    repo = PostgresProfileRepository()
    profile = StudentProfile(**VALID_PROFILE)

    # save_profile calls _engine() → conftest guard raises AssertionError
    # → save_profile wraps it as RuntimeError (expected behaviour of the wrapper)
    with pytest.raises(RuntimeError, match="AssertionError"):
        repo.save_profile("isolation-test-user", profile)
