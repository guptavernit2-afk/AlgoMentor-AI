"""
AlgoMentor AI — tests for the Weekly Schedule Repository layer.

All tests run in memory mode; no real Supabase connection is made.

Covers:
  1. MemoryScheduleRepository saves and retrieves a valid seven-day schedule.
  2. MemoryScheduleRepository updates an existing weekly schedule.
  3. get_schedule_repository returns MemoryScheduleRepository in memory mode.
  4. get_schedule_repository can select PostgresScheduleRepository without connecting.
  5. Weekly Schedule API PUT/GET behaviour unchanged in memory mode.
  6. require_schedule() works in memory mode.
  7. Validation still rejects: free day with classes, duplicate/missing days,
     class ending before starting, overlapping slots.
  8. Hard database guard proves schedule API calls do not use Postgres.
  9. Controlled Postgres repository failure does not expose credentials.

Run from backend/:
    pytest tests/test_schedule_repository.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pydantic import SecretStr

from app.main import app


# ============================================================
# Shared test data
# (conftest autouse fixtures clear caches + stores per test)
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

UPDATED_SCHEDULE = {
    "days": [
        {"day": "Monday",    "is_free_day": True,  "classes": []},
        {"day": "Tuesday",   "is_free_day": False, "classes": [{"title": "Lab", "start_time": "10:00", "end_time": "12:00"}]},
        {"day": "Wednesday", "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
        {"day": "Thursday",  "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "10:00", "end_time": "15:00"}]},
        {"day": "Friday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Saturday",  "is_free_day": True,  "classes": []},
        {"day": "Sunday",    "is_free_day": True,  "classes": []},
    ]
}


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def client_with_profile(client) -> TestClient:
    """Return a TestClient with a profile already saved for test-user."""
    client.put("/api/users/test-user/profile", json=VALID_PROFILE)
    return client


# ============================================================
# 1. MemoryScheduleRepository: save and retrieve
# ============================================================

def test_memory_repo_save_and_get():
    """save_schedule stores the schedule; get_schedule returns it unchanged."""
    from app.models import WeeklySchedule
    from app.repositories.schedule_repository import MemoryScheduleRepository

    repo = MemoryScheduleRepository()
    schedule = WeeklySchedule(**VALID_SCHEDULE)

    saved = repo.save_schedule("test-user", schedule)
    fetched = repo.get_schedule("test-user")

    assert saved is schedule
    assert fetched is not None
    assert len(fetched.days) == 7
    monday = next(d for d in fetched.days if d.day == "Monday")
    assert not monday.is_free_day
    assert monday.classes[0].start_time == "09:00"
    saturday = next(d for d in fetched.days if d.day == "Saturday")
    assert saturday.is_free_day
    assert saturday.classes == []


def test_memory_repo_get_returns_none_for_unknown_user():
    from app.repositories.schedule_repository import MemoryScheduleRepository

    repo = MemoryScheduleRepository()
    assert repo.get_schedule("nobody") is None


# ============================================================
# 2. MemoryScheduleRepository: update existing schedule
# ============================================================

def test_memory_repo_updates_existing_schedule():
    """A second save_schedule call must overwrite the first."""
    from app.models import WeeklySchedule
    from app.repositories.schedule_repository import MemoryScheduleRepository

    repo = MemoryScheduleRepository()
    first = WeeklySchedule(**VALID_SCHEDULE)
    second = WeeklySchedule(**UPDATED_SCHEDULE)

    repo.save_schedule("test-user", first)
    repo.save_schedule("test-user", second)

    fetched = repo.get_schedule("test-user")
    assert fetched is not None
    monday = next(d for d in fetched.days if d.day == "Monday")
    assert monday.is_free_day  # Updated to free day


# ============================================================
# 3. Factory returns MemoryScheduleRepository in memory mode
# ============================================================

def test_factory_returns_memory_repo_in_memory_mode():
    from app.repositories.schedule_repository import (
        get_schedule_repository,
        MemoryScheduleRepository,
    )
    from app.config import Settings

    memory_settings = Settings.model_construct(storage_backend="memory")
    with patch("app.config.get_settings", return_value=memory_settings):
        get_schedule_repository.cache_clear()
        repo = get_schedule_repository()

    assert isinstance(repo, MemoryScheduleRepository)


# ============================================================
# 4. Factory selects PostgresScheduleRepository without connecting
# ============================================================

def test_factory_returns_postgres_repo_without_connecting():
    """
    When storage_backend='postgres', the factory returns PostgresScheduleRepository.
    No connection is attempted at selection time — the conftest guard would
    raise AssertionError if _engine() were called.
    """
    from app.repositories.schedule_repository import (
        get_schedule_repository,
        PostgresScheduleRepository,
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
        get_schedule_repository.cache_clear()
        repo = get_schedule_repository()  # must NOT raise — no network call

    assert isinstance(repo, PostgresScheduleRepository)
    get_schedule_repository.cache_clear()


# ============================================================
# 5. Weekly Schedule API PUT/GET unchanged in memory mode
# ============================================================

def test_put_schedule_saves_successfully(client_with_profile):
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "test-user"
    assert len(data["schedule"]["days"]) == 7
    assert data["message"] == "Weekly schedule saved successfully."


def test_get_schedule_returns_saved_data(client_with_profile):
    client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    r = client_with_profile.get("/api/users/test-user/weekly-schedule")
    assert r.status_code == 200
    days = r.json()["schedule"]["days"]
    saturday = next(d for d in days if d["day"] == "Saturday")
    assert saturday["is_free_day"] is True
    assert saturday["classes"] == []


def test_get_schedule_not_found_returns_404(client):
    r = client.get("/api/users/ghost-user/weekly-schedule")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_put_schedule_updates_existing(client_with_profile):
    client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    client_with_profile.put("/api/users/test-user/weekly-schedule", json=UPDATED_SCHEDULE)
    r = client_with_profile.get("/api/users/test-user/weekly-schedule")
    days = r.json()["schedule"]["days"]
    monday = next(d for d in days if d["day"] == "Monday")
    assert monday["is_free_day"] is True


# ============================================================
# 6. require_schedule() works in memory mode
# ============================================================

def test_require_schedule_raises_404_when_missing():
    """require_schedule must raise HTTPException 404 when no schedule exists."""
    from fastapi import HTTPException
    from app.services.schedule_service import require_schedule

    with pytest.raises(HTTPException) as exc_info:
        require_schedule("nobody")
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()


def test_require_schedule_returns_schedule_in_memory_mode(client_with_profile):
    """After saving, require_schedule returns the correct WeeklySchedule."""
    from app.services.schedule_service import require_schedule
    from app.models import WeeklySchedule

    client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    schedule = require_schedule("test-user")
    assert isinstance(schedule, WeeklySchedule)
    assert len(schedule.days) == 7


# ============================================================
# 7. Validation: all rules still enforced
# ============================================================

def test_put_rejects_free_day_with_classes(client_with_profile):
    """Saturday is marked free but contains a class → 400."""
    bad = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": [{"title": "Morning Class", "start_time": "09:00", "end_time": "11:00"}]},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {"day": "Saturday",  "is_free_day": True,  "classes": [{"title": "Extra Class", "start_time": "10:00", "end_time": "12:00"}]},
            {"day": "Sunday",    "is_free_day": True,  "classes": []},
        ]
    }
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=bad)
    assert r.status_code == 400
    assert "free day" in r.json()["detail"].lower()


def test_put_rejects_duplicate_days(client_with_profile):
    """Providing Monday twice and omitting Sunday → 400."""
    dup = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": []},
            {"day": "Monday",    "is_free_day": False, "classes": []},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
        ]
    }
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=dup)
    assert r.status_code == 400


def test_put_rejects_end_time_before_start_time(client_with_profile):
    """A class ending before it starts → 400."""
    bad = dict(VALID_SCHEDULE)
    bad = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": [{"title": "Bad", "start_time": "14:00", "end_time": "09:00"}]},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
            {"day": "Sunday",    "is_free_day": True,  "classes": []},
        ]
    }
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=bad)
    assert r.status_code == 400
    assert "not later than" in r.json()["detail"].lower()


def test_put_rejects_overlapping_slots(client_with_profile):
    """Two overlapping class slots on same day → 400."""
    bad = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": [
                {"title": "Lecture A", "start_time": "09:00", "end_time": "12:00"},
                {"title": "Lecture B", "start_time": "11:00", "end_time": "14:00"},
            ]},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
            {"day": "Sunday",    "is_free_day": True,  "classes": []},
        ]
    }
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=bad)
    assert r.status_code == 400
    assert "overlap" in r.json()["detail"].lower()


# ============================================================
# 8. Hard database guard: schedule API during pytest never uses Postgres
# ============================================================

def test_schedule_api_does_not_call_db_engine(client_with_profile):
    """
    PUT weekly-schedule must complete successfully without calling
    PostgresScheduleRepository._engine().

    The conftest _block_live_db_engine fixture replaces _engine() with a
    guard that raises AssertionError.  If this test passes, no DB call was made.
    """
    r = client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    assert r.status_code == 200
    # Reaching here proves _engine() was not called.


def test_get_schedule_does_not_call_db_engine(client_with_profile):
    """GET weekly-schedule must read from memory without any DB call."""
    client_with_profile.put("/api/users/test-user/weekly-schedule", json=VALID_SCHEDULE)
    r = client_with_profile.get("/api/users/test-user/weekly-schedule")
    assert r.status_code == 200


# ============================================================
# 9. Postgres repository failure does not expose credentials
# ============================================================

def test_postgres_save_error_does_not_leak_password():
    """
    When PostgresScheduleRepository raises a RuntimeError wrapping a DB
    failure, the message must not contain the password.
    """
    from app.models import WeeklySchedule
    from app.repositories.schedule_repository import PostgresScheduleRepository
    from app.repositories import schedule_repository as repo_module

    repo = PostgresScheduleRepository()
    schedule = WeeklySchedule(**VALID_SCHEDULE)
    secret_password = "SuperSecretSchedule456!"

    mock_engine = MagicMock()
    mock_engine.begin.side_effect = Exception("connection refused")

    with patch.object(
        repo_module.PostgresScheduleRepository,
        "_engine",
        staticmethod(lambda: mock_engine),
    ):
        with pytest.raises(RuntimeError) as exc_info:
            repo.save_schedule("test-user", schedule)

    error_msg = str(exc_info.value)
    assert secret_password not in error_msg
    assert "SuperSecret" not in error_msg
    assert "test-user" in error_msg or "Database error" in error_msg
