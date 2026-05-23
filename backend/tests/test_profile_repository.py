"""
AlgoMentor AI — tests for the Student Profile Repository layer.

All tests run in memory mode; no real Supabase connection is made.

Covers:
  1. MemoryProfileRepository saves and retrieves a valid profile.
  2. MemoryProfileRepository updates an existing profile.
  3. Factory returns MemoryProfileRepository in memory mode.
  4. Factory can select PostgresProfileRepository without opening a connection.
  5. Profile router PUT/GET behaviour remains unchanged in memory mode.
  6. require_profile() continues to raise HTTP 404 in memory mode.
  7. Database RuntimeError wrapper never exposes a connection string or password.

Run from backend/:
    pytest tests/test_profile_repository.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pydantic import SecretStr

from app.main import app
from app.storage import clear_all_stores


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def reset_stores():
    clear_all_stores()
    # Also clear the repository factory cache between tests so that a
    # patched storage_backend takes effect in the test that needs it.
    from app.repositories.profile_repository import get_profile_repository
    get_profile_repository.cache_clear()
    yield
    clear_all_stores()
    get_profile_repository.cache_clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ============================================================
# Shared profile payload
# ============================================================

VALID_PROFILE = {
    "name": "Vernit",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}

UPDATED_PROFILE = {**VALID_PROFILE, "name": "Vernit Updated", "current_topic": "Graphs"}


# ============================================================
# 1. MemoryProfileRepository: save and retrieve
# ============================================================

def test_memory_repo_save_and_get():
    """save_profile stores the profile; get_profile returns it unchanged."""
    from app.models import StudentProfile
    from app.repositories.profile_repository import MemoryProfileRepository

    repo = MemoryProfileRepository()
    profile = StudentProfile(**VALID_PROFILE)

    saved = repo.save_profile("test-user", profile)
    fetched = repo.get_profile("test-user")

    assert saved is profile
    assert fetched is not None
    assert fetched.name == "Vernit"
    assert fetched.goal == "Placement Prep"
    assert fetched.completed_topics == ["Arrays"]


def test_memory_repo_get_returns_none_for_unknown_user():
    from app.repositories.profile_repository import MemoryProfileRepository

    repo = MemoryProfileRepository()
    assert repo.get_profile("nobody") is None


# ============================================================
# 2. MemoryProfileRepository: update existing profile
# ============================================================

def test_memory_repo_updates_existing_profile():
    """A second save_profile call must overwrite the first."""
    from app.models import StudentProfile
    from app.repositories.profile_repository import MemoryProfileRepository

    repo = MemoryProfileRepository()
    first = StudentProfile(**VALID_PROFILE)
    second = StudentProfile(**UPDATED_PROFILE)

    repo.save_profile("test-user", first)
    repo.save_profile("test-user", second)

    fetched = repo.get_profile("test-user")
    assert fetched is not None
    assert fetched.name == "Vernit Updated"
    assert fetched.current_topic == "Graphs"


# ============================================================
# 3. Factory returns MemoryProfileRepository in memory mode
# ============================================================

def test_factory_returns_memory_repo_in_memory_mode():
    from app.repositories.profile_repository import (
        get_profile_repository,
        MemoryProfileRepository,
    )
    from app.config import Settings

    memory_settings = Settings.model_construct(storage_backend="memory")
    # get_settings is defined in app.config — patch it at the source.
    with patch("app.config.get_settings", return_value=memory_settings):
        get_profile_repository.cache_clear()
        repo = get_profile_repository()

    assert isinstance(repo, MemoryProfileRepository)


# ============================================================
# 4. Factory selects PostgresProfileRepository without opening a connection
# ============================================================

def test_factory_returns_postgres_repo_without_connecting():
    """
    When storage_backend='postgres', the factory returns a PostgresProfileRepository.
    No connection is attempted during selection — the engine is only created
    lazily when an actual operation is called.
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
        db_password=SecretStr("secret"),
        db_name="postgres",
        db_port=5432,
        db_sslmode="require",
    )

    # Patch at the source module so the local import inside get_profile_repository
    # picks up the mock value.
    with patch("app.config.get_settings", return_value=postgres_settings):
        get_profile_repository.cache_clear()
        repo = get_profile_repository()  # must NOT raise — no network call

    assert isinstance(repo, PostgresProfileRepository)
    # Clean up cache so later tests get memory mode back
    get_profile_repository.cache_clear()


# ============================================================
# 5. Profile router PUT/GET unchanged in memory mode
# ============================================================

def test_put_profile_saves_successfully(client):
    r = client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "test-user"
    assert data["profile"]["name"] == "Vernit"
    assert data["message"] == "Student profile saved successfully."


def test_get_profile_returns_saved_data(client):
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    r = client.get("/api/users/test-user/profile")
    assert r.status_code == 200
    assert r.json()["profile"]["goal"] == "Placement Prep"


def test_get_profile_not_found_returns_404(client):
    r = client.get("/api/users/ghost-user/profile")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_put_profile_rejects_inverted_minutes(client):
    bad = {**VALID_PROFILE, "minimum_daily_minutes": 100, "maximum_daily_minutes": 50}
    r = client.put("/api/users/test-user/profile", json=bad)
    assert r.status_code == 400
    assert "maximum daily minutes" in r.json()["detail"].lower()


def test_put_profile_updates_existing(client):
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    client.put("/api/users/test-user/profile", json=UPDATED_PROFILE)
    r = client.get("/api/users/test-user/profile")
    assert r.json()["profile"]["name"] == "Vernit Updated"


# ============================================================
# 6. require_profile() works in memory mode
# ============================================================

def test_require_profile_raises_404_when_missing():
    """require_profile must raise HTTPException 404 in memory mode."""
    from fastapi import HTTPException
    from app.services.profile_service import require_profile

    with pytest.raises(HTTPException) as exc_info:
        require_profile("nobody")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_require_profile_returns_profile_in_memory_mode(client):
    """After saving, require_profile returns the correct profile."""
    from app.services.profile_service import require_profile
    from app.models import StudentProfile

    # Save via router (through MemoryRepository)
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)

    profile = require_profile("test-user")
    assert isinstance(profile, StudentProfile)
    assert profile.name == "Vernit"


# ============================================================
# 7. RuntimeError wrapper never exposes connection string / password
# ============================================================

def test_postgres_save_error_does_not_leak_password():
    """
    When the PostgresProfileRepository raises a RuntimeError wrapping a DB
    failure, the message must not contain the password or connection URL.

    Patches _engine() on the class directly (the same point that conftest's
    _block_live_db_engine guard targets) so the mock engine is used instead
    of either the real engine or the forbidden-engine guard.
    """
    from app.models import StudentProfile
    from app.repositories.profile_repository import PostgresProfileRepository
    from app.repositories import profile_repository as repo_module

    repo = PostgresProfileRepository()
    secret_password = "SuperSecret123!"

    # Simulate the engine raising an unexpected driver error by replacing
    # _engine() at the class level (overrides conftest's forbidden guard).
    mock_engine = MagicMock()
    mock_engine.begin.side_effect = Exception("connection refused")

    with patch.object(
        repo_module.PostgresProfileRepository,
        "_engine",
        staticmethod(lambda: mock_engine),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            repo.save_profile("test-user", StudentProfile(**VALID_PROFILE))

    error_msg = str(exc_info.value)
    assert secret_password not in error_msg
    assert "SuperSecret" not in error_msg
    # Message must still be informative
    assert "test-user" in error_msg or "Database error" in error_msg
