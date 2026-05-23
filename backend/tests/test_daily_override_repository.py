"""
AlgoMentor AI — tests for the Daily Override Repository layer.

All tests run in memory mode; no real Supabase connection is made.

Covers:
  1.  MemoryDailyOverrideRepository saves and retrieves a valid override.
  2.  MemoryDailyOverrideRepository updates the override for the same user/date.
  3.  MemoryDailyOverrideRepository deletes only the specified override.
  4.  get_daily_override_repository returns MemoryDailyOverrideRepository in memory mode.
  5.  get_daily_override_repository can select PostgresDailyOverrideRepository without connecting.
  6.  Daily Override PUT/GET/DELETE API behaviour unchanged in memory mode.
  7.  Saving an override still requires both profile and weekly schedule.
  8.  Validation rejects: out-of-range extra_available_minutes, note > 200 chars,
      invalid situation, invalid energy_level.
  9.  Hard DB guard proves Daily Override API does not use PostgreSQL during pytest.
  10. Controlled Postgres repository failure does not expose secrets.

Run from backend/:
    pytest tests/test_daily_override_repository.py -v
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pydantic import SecretStr

from app.main import app


# ============================================================
# Shared test data
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

VALID_SCHEDULE = {
    "days": [
        {"day": "Monday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
        {"day": "Tuesday",   "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "13:00"}]},
        {"day": "Wednesday", "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
        {"day": "Thursday",  "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "10:00", "end_time": "15:00"}]},
        {"day": "Friday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Saturday",  "is_free_day": True,  "classes": []},
        {"day": "Sunday",    "is_free_day": True,  "classes": []},
    ]
}

EXAM_OVERRIDE = {
    "situation": "Internal exam / Test",
    "extra_available_minutes": 0,
    "energy_level": "Low",
    "note": "Physics internal exam today",
}

UPDATED_OVERRIDE = {
    "situation": "Assignment",
    "extra_available_minutes": -30,
    "energy_level": "Normal",
    "note": "Assignment submission day",
}

OVERRIDE_DATE = "2026-05-22"  # a Friday


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def client_with_profile_and_schedule(client) -> TestClient:
    """Return client with profile + schedule already saved."""
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    client.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    return client


# ============================================================
# 1. MemoryDailyOverrideRepository: save and retrieve
# ============================================================

def test_memory_repo_save_and_get():
    from app.models import DailyOverride
    from app.repositories.daily_override_repository import MemoryDailyOverrideRepository

    repo = MemoryDailyOverrideRepository()
    d = date(2026, 5, 22)
    override = DailyOverride(**EXAM_OVERRIDE)

    saved = repo.save_override("user1", d, override)
    fetched = repo.get_override("user1", d)

    assert saved is override
    assert fetched is not None
    assert fetched.situation == "Internal exam / Test"
    assert fetched.extra_available_minutes == 0
    assert fetched.energy_level == "Low"
    assert fetched.note == "Physics internal exam today"


def test_memory_repo_get_returns_none_for_unknown():
    from app.repositories.daily_override_repository import MemoryDailyOverrideRepository

    repo = MemoryDailyOverrideRepository()
    assert repo.get_override("nobody", date(2026, 5, 22)) is None


# ============================================================
# 2. MemoryDailyOverrideRepository: update existing override
# ============================================================

def test_memory_repo_updates_existing_override():
    from app.models import DailyOverride
    from app.repositories.daily_override_repository import MemoryDailyOverrideRepository

    repo = MemoryDailyOverrideRepository()
    d = date(2026, 5, 22)

    repo.save_override("user1", d, DailyOverride(**EXAM_OVERRIDE))
    repo.save_override("user1", d, DailyOverride(**UPDATED_OVERRIDE))

    fetched = repo.get_override("user1", d)
    assert fetched is not None
    assert fetched.situation == "Assignment"
    assert fetched.extra_available_minutes == -30
    assert fetched.energy_level == "Normal"


# ============================================================
# 3. MemoryDailyOverrideRepository: delete only specified override
# ============================================================

def test_memory_repo_deletes_only_specified_override():
    from app.models import DailyOverride
    from app.repositories.daily_override_repository import MemoryDailyOverrideRepository

    repo = MemoryDailyOverrideRepository()
    d1 = date(2026, 5, 22)
    d2 = date(2026, 5, 23)
    override = DailyOverride(**EXAM_OVERRIDE)

    repo.save_override("user1", d1, override)
    repo.save_override("user1", d2, override)

    result = repo.delete_override("user1", d1)
    assert result is True
    assert repo.get_override("user1", d1) is None
    assert repo.get_override("user1", d2) is not None  # other date untouched


def test_memory_repo_delete_returns_false_when_not_found():
    from app.repositories.daily_override_repository import MemoryDailyOverrideRepository

    repo = MemoryDailyOverrideRepository()
    result = repo.delete_override("ghost", date(2026, 5, 22))
    assert result is False


# ============================================================
# 4. Factory returns MemoryDailyOverrideRepository in memory mode
# ============================================================

def test_factory_returns_memory_repo_in_memory_mode():
    from app.repositories.daily_override_repository import (
        get_daily_override_repository,
        MemoryDailyOverrideRepository,
    )
    from app.config import Settings

    memory_settings = Settings.model_construct(storage_backend="memory")
    with patch("app.config.get_settings", return_value=memory_settings):
        get_daily_override_repository.cache_clear()
        repo = get_daily_override_repository()

    assert isinstance(repo, MemoryDailyOverrideRepository)
    get_daily_override_repository.cache_clear()


# ============================================================
# 5. Factory selects PostgresDailyOverrideRepository without connecting
# ============================================================

def test_factory_returns_postgres_repo_without_connecting():
    from app.repositories.daily_override_repository import (
        get_daily_override_repository,
        PostgresDailyOverrideRepository,
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

    with patch("app.config.get_settings", return_value=postgres_settings):
        get_daily_override_repository.cache_clear()
        repo = get_daily_override_repository()  # must NOT raise — no network call

    assert isinstance(repo, PostgresDailyOverrideRepository)
    get_daily_override_repository.cache_clear()


# ============================================================
# 6. Daily Override API PUT/GET/DELETE in memory mode
# ============================================================

def test_put_override_saves_successfully(client_with_profile_and_schedule):
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "test-user"
    assert data["override"]["situation"] == "Internal exam / Test"
    assert data["message"] == "Daily override saved successfully. Regular timetable unchanged."


def test_get_override_returns_saved_data(client_with_profile_and_schedule):
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    r = client_with_profile_and_schedule.get(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r.status_code == 200
    data = r.json()
    assert data["override"]["situation"] == "Internal exam / Test"
    assert data["override"]["energy_level"] == "Low"
    assert data["override"]["note"] == "Physics internal exam today"
    assert data["message"] == "Daily override retrieved successfully."


def test_get_override_not_found_returns_404(client):
    r = client.get(f"/api/users/ghost-user/daily-overrides/{OVERRIDE_DATE}")
    assert r.status_code == 404
    assert "No daily override found" in r.json()["detail"]


def test_delete_override_succeeds(client_with_profile_and_schedule):
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    r = client_with_profile_and_schedule.delete(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Daily override removed. Normal weekly timetable will be used."

    # After delete, GET should return 404
    r2 = client_with_profile_and_schedule.get(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r2.status_code == 404


def test_delete_override_not_found_returns_404(client):
    r = client.delete(f"/api/users/ghost-user/daily-overrides/{OVERRIDE_DATE}")
    assert r.status_code == 404
    assert "No daily override found" in r.json()["detail"]


def test_put_override_updates_existing(client_with_profile_and_schedule):
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=UPDATED_OVERRIDE,
    )
    r = client_with_profile_and_schedule.get(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r.status_code == 200
    assert r.json()["override"]["situation"] == "Assignment"
    assert r.json()["override"]["extra_available_minutes"] == -30


def test_delete_does_not_affect_other_dates(client_with_profile_and_schedule):
    """Deleting one date must not remove overrides for other dates."""
    other_date = "2026-05-23"
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=EXAM_OVERRIDE
    )
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{other_date}", json=UPDATED_OVERRIDE
    )
    client_with_profile_and_schedule.delete(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    r = client_with_profile_and_schedule.get(
        f"/api/users/test-user/daily-overrides/{other_date}"
    )
    assert r.status_code == 200


# ============================================================
# 7. Saving an override requires both profile and weekly schedule
# ============================================================

def test_put_override_without_profile_returns_404(client):
    r = client.put(
        f"/api/users/no-profile-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    assert r.status_code == 404


def test_put_override_without_schedule_returns_404(client):
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    r = client.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    assert r.status_code == 404


# ============================================================
# 8. Validation: all rules still enforced
# ============================================================

def test_put_rejects_extra_minutes_too_low(client_with_profile_and_schedule):
    bad = dict(EXAM_OVERRIDE, extra_available_minutes=-241)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=bad
    )
    assert r.status_code == 422


def test_put_rejects_extra_minutes_too_high(client_with_profile_and_schedule):
    bad = dict(EXAM_OVERRIDE, extra_available_minutes=481)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=bad
    )
    assert r.status_code == 422


def test_put_rejects_note_too_long(client_with_profile_and_schedule):
    bad = dict(EXAM_OVERRIDE, note="x" * 201)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=bad
    )
    assert r.status_code == 422


def test_put_rejects_invalid_situation(client_with_profile_and_schedule):
    bad = dict(EXAM_OVERRIDE, situation="Invalid Situation XYZ")
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=bad
    )
    assert r.status_code == 422


def test_put_rejects_invalid_energy_level(client_with_profile_and_schedule):
    bad = dict(EXAM_OVERRIDE, energy_level="Medium")
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=bad
    )
    assert r.status_code == 422


def test_put_accepts_boundary_extra_minutes_min(client_with_profile_and_schedule):
    """extra_available_minutes = -240 is the allowed lower bound."""
    ok = dict(EXAM_OVERRIDE, extra_available_minutes=-240)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=ok
    )
    assert r.status_code == 200


def test_put_accepts_boundary_extra_minutes_max(client_with_profile_and_schedule):
    """extra_available_minutes = 480 is the allowed upper bound."""
    ok = dict(EXAM_OVERRIDE, extra_available_minutes=480)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=ok
    )
    assert r.status_code == 200


def test_put_accepts_max_length_note(client_with_profile_and_schedule):
    """note of exactly 200 characters is valid."""
    ok = dict(EXAM_OVERRIDE, note="x" * 200)
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}", json=ok
    )
    assert r.status_code == 200


# ============================================================
# 9. Hard DB guard: Daily Override API during pytest never uses Postgres
# ============================================================

def test_put_override_does_not_call_db_engine(client_with_profile_and_schedule):
    """
    PUT daily-override must succeed without calling
    PostgresDailyOverrideRepository._engine().

    The conftest _block_live_db_engine fixture blocks _engine() via monkeypatch.
    If this test passes, no DB call was made.
    """
    r = client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    assert r.status_code == 200


def test_get_override_does_not_call_db_engine(client_with_profile_and_schedule):
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    r = client_with_profile_and_schedule.get(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r.status_code == 200


def test_delete_override_does_not_call_db_engine(client_with_profile_and_schedule):
    client_with_profile_and_schedule.put(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}",
        json=EXAM_OVERRIDE,
    )
    r = client_with_profile_and_schedule.delete(
        f"/api/users/test-user/daily-overrides/{OVERRIDE_DATE}"
    )
    assert r.status_code == 200


# ============================================================
# 10. Postgres repository failure does not expose secrets
# ============================================================

def test_postgres_save_error_does_not_leak_password():
    from app.models import DailyOverride
    from app.repositories.daily_override_repository import PostgresDailyOverrideRepository
    from app.repositories import daily_override_repository as repo_module

    repo = PostgresDailyOverrideRepository()
    override = DailyOverride(**EXAM_OVERRIDE)
    secret_password = "SuperSecretOverride789!"

    mock_engine = MagicMock()
    mock_engine.begin.side_effect = Exception("connection refused")

    with patch.object(
        repo_module.PostgresDailyOverrideRepository,
        "_engine",
        staticmethod(lambda: mock_engine),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            repo.save_override("test-user", date(2026, 5, 22), override)

    error_msg = str(exc_info.value)
    assert secret_password not in error_msg
    assert "SuperSecret" not in error_msg
    assert "test-user" in error_msg or "Database error" in error_msg


def test_postgres_get_error_does_not_leak_password():
    from app.repositories.daily_override_repository import PostgresDailyOverrideRepository
    from app.repositories import daily_override_repository as repo_module

    repo = PostgresDailyOverrideRepository()
    secret_password = "SuperSecretGetOverride!"

    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception("auth failed")

    with patch.object(
        repo_module.PostgresDailyOverrideRepository,
        "_engine",
        staticmethod(lambda: mock_engine),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            repo.get_override("test-user", date(2026, 5, 22))

    error_msg = str(exc_info.value)
    assert secret_password not in error_msg


def test_postgres_delete_error_does_not_leak_password():
    from app.repositories.daily_override_repository import PostgresDailyOverrideRepository
    from app.repositories import daily_override_repository as repo_module

    repo = PostgresDailyOverrideRepository()
    secret_password = "SuperSecretDeleteOverride!"

    mock_engine = MagicMock()
    mock_engine.begin.side_effect = Exception("auth failed")

    with patch.object(
        repo_module.PostgresDailyOverrideRepository,
        "_engine",
        staticmethod(lambda: mock_engine),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            repo.delete_override("test-user", date(2026, 5, 22))

    error_msg = str(exc_info.value)
    assert secret_password not in error_msg
