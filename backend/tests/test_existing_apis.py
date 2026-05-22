"""
AlgoMentor AI — test suite for all existing API endpoints.

Run from the backend/ directory:

    pytest -q

Each test function gets a fresh in-memory state via the autouse
`reset_stores` fixture, so tests are fully independent.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import clear_all_stores


# ============================================================
# Client fixture and state reset
# ============================================================

@pytest.fixture(autouse=True)
def reset_stores():
    """Clear all in-memory stores before every test."""
    clear_all_stores()
    yield
    clear_all_stores()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ============================================================
# Shared test data
# ============================================================

DEMO_PROFILE = {
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


def _save_demo_profile_and_schedule(client: TestClient) -> None:
    """Helper: persist demo profile + weekly schedule for user demo-user."""
    client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    client.put("/api/users/demo-user/weekly-schedule", json=VALID_SCHEDULE)


# ============================================================
# A. Health check
# ============================================================

def test_health_returns_healthy(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_returns_running_message(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "AlgoMentor AI backend is running"}


# ============================================================
# B. Recommendation endpoint
# ============================================================

def test_recommendations_high_workload_exam_prioritises_easy(client):
    """High workload + Internal exam should rank an Easy problem first."""
    payload = {
        "workload": "High",
        "situation": "Internal exam / Test",
        "weak_concept": "Prefix Sum",
        "goal": "Placement Prep",
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    recommendations = data["recommendations"]

    # Top-ranked problem must be Easy.
    assert recommendations[0]["difficulty"] == "Easy"

    # plan_note must reference exam day / light practice.
    plan_note: str = data["plan_note"].lower()
    assert "exam" in plan_note or "light" in plan_note


def test_recommendations_low_workload_free_day_ranks_subarray_sum_first(client):
    """Low workload + Free day + Prefix Sum + Competitive Programming → Subarray Sum Equals K first."""
    payload = {
        "workload": "Low",
        "situation": "Free day",
        "weak_concept": "Prefix Sum",
        "goal": "Competitive Programming",
    }
    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    recommendations = response.json()["recommendations"]
    assert recommendations[0]["title"] == "Subarray Sum Equals K"


# ============================================================
# C. Student profile lifecycle
# ============================================================

def test_put_valid_profile_succeeds(client):
    response = client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "demo-user"
    assert data["profile"]["name"] == "Vernit"
    assert "saved successfully" in data["message"]


def test_get_profile_returns_same_data(client):
    client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    response = client.get("/api/users/demo-user/profile")
    assert response.status_code == 200
    assert response.json()["profile"]["goal"] == "Placement Prep"


def test_get_profile_not_found_returns_404(client):
    response = client.get("/api/users/unknown-user/profile")
    assert response.status_code == 404


def test_put_profile_rejects_invalid_minutes(client):
    """maximum_daily_minutes < minimum_daily_minutes must return 400."""
    bad_profile = {**DEMO_PROFILE, "minimum_daily_minutes": 120, "maximum_daily_minutes": 60}
    response = client.put("/api/users/demo-user/profile", json=bad_profile)
    assert response.status_code == 400
    assert "maximum" in response.json()["detail"].lower()


# ============================================================
# D. Weekly schedule lifecycle
# ============================================================

def test_put_valid_schedule_succeeds(client):
    client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    response = client.put("/api/users/demo-user/weekly-schedule", json=VALID_SCHEDULE)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "demo-user"
    assert len(data["schedule"]["days"]) == 7
    assert "saved successfully" in data["message"]


def test_get_weekly_schedule_returns_saved_data(client):
    client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    client.put("/api/users/demo-user/weekly-schedule", json=VALID_SCHEDULE)
    response = client.get("/api/users/demo-user/weekly-schedule")
    assert response.status_code == 200
    days = response.json()["schedule"]["days"]
    assert any(d["day"] == "Saturday" and d["is_free_day"] is True for d in days)


def test_put_schedule_rejects_free_day_with_classes(client):
    """Saturday marked is_free_day=True but also has a class → 400."""
    invalid_schedule = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {
                "day": "Saturday",
                "is_free_day": True,
                "classes": [{"title": "Extra class", "start_time": "10:00", "end_time": "12:00"}],
            },
            {"day": "Sunday", "is_free_day": True, "classes": []},
        ]
    }
    response = client.put("/api/users/demo-user/weekly-schedule", json=invalid_schedule)
    assert response.status_code == 400


def test_put_schedule_rejects_duplicate_days(client):
    """Providing Monday twice and omitting Sunday must return 400."""
    dup_schedule = {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": []},
            {"day": "Monday",    "is_free_day": False, "classes": []},  # duplicate
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": []},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
        ]
    }
    response = client.put("/api/users/demo-user/weekly-schedule", json=dup_schedule)
    assert response.status_code == 400


# ============================================================
# E. Daily override lifecycle
# ============================================================

OVERRIDE_DATE = "2026-05-22"
OVERRIDE_BODY = {
    "situation": "Internal exam / Test",
    "extra_available_minutes": 0,
    "energy_level": "Low",
    "note": "Physics internal exam today",
}


def test_put_override_without_profile_returns_404(client):
    """Saving an override before creating a profile must be rejected."""
    response = client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    assert response.status_code == 404


def test_put_override_without_schedule_returns_404(client):
    """Saving an override before saving a schedule must be rejected."""
    client.put("/api/users/demo-user/profile", json=DEMO_PROFILE)
    response = client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    assert response.status_code == 404


def test_put_override_succeeds(client):
    _save_demo_profile_and_schedule(client)
    response = client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "demo-user"
    assert data["date"] == OVERRIDE_DATE
    assert data["override"]["situation"] == "Internal exam / Test"
    assert data["override"]["note"] == "Physics internal exam today"
    assert "Regular timetable unchanged" in data["message"]


def test_get_override_returns_saved_data(client):
    _save_demo_profile_and_schedule(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    response = client.get(f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}")
    assert response.status_code == 200
    data = response.json()
    assert data["override"]["energy_level"] == "Low"
    assert data["override"]["extra_available_minutes"] == 0


def test_weekly_schedule_unchanged_after_override(client):
    """Saving an override must not alter the stored weekly schedule."""
    _save_demo_profile_and_schedule(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    response = client.get("/api/users/demo-user/weekly-schedule")
    assert response.status_code == 200
    days = response.json()["schedule"]["days"]
    saturday = next(d for d in days if d["day"] == "Saturday")
    sunday = next(d for d in days if d["day"] == "Sunday")
    assert saturday["is_free_day"] is True
    assert saturday["classes"] == []
    assert sunday["is_free_day"] is True


def test_delete_override_returns_correct_message(client):
    _save_demo_profile_and_schedule(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    response = client.delete(f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}")
    assert response.status_code == 200
    assert response.json()["message"] == (
        "Daily override removed. Normal weekly timetable will be used."
    )


def test_get_deleted_override_returns_404(client):
    _save_demo_profile_and_schedule(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}",
        json=OVERRIDE_BODY,
    )
    client.delete(f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}")
    response = client.get(f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}")
    assert response.status_code == 404


def test_delete_nonexistent_override_returns_404(client):
    _save_demo_profile_and_schedule(client)
    response = client.delete(f"/api/users/demo-user/daily-overrides/{OVERRIDE_DATE}")
    assert response.status_code == 404
