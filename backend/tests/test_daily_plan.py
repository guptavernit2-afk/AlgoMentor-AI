"""
AlgoMentor AI — tests for the Smart Daily Plan endpoint.

Also covers the new schedule validation rules (end_time > start_time,
no overlapping slots on the same day).

Run from backend/ directory:

    pytest tests/test_daily_plan.py -v
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import clear_all_stores


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def reset_stores():
    """Isolate every test by clearing all in-memory stores."""
    clear_all_stores()
    yield
    clear_all_stores()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ============================================================
# Shared test data
# ============================================================

PLACEMENT_PROFILE = {
    "name": "Vernit",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}

COMPETITIVE_PROFILE = {
    "name": "Vernit",
    "goal": "Competitive Programming",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}

# Standard week: Mon–Fri 09:00–14:00, Sat–Sun free
STANDARD_SCHEDULE = {
    "days": [
        {"day": "Monday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Tuesday",   "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Wednesday", "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Thursday",  "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Friday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Saturday",  "is_free_day": True,  "classes": []},
        {"day": "Sunday",    "is_free_day": True,  "classes": []},
    ]
}

# 2026-05-22 → Friday;  2026-05-23 → Saturday
FRIDAY_DATE   = "2026-05-22"
SATURDAY_DATE = "2026-05-23"


def _setup(client: TestClient, profile: dict = PLACEMENT_PROFILE) -> None:
    """Persist profile + standard schedule for demo-user."""
    r = client.put("/api/users/demo-user/profile", json=profile)
    assert r.status_code == 200
    r = client.put("/api/users/demo-user/weekly-schedule", json=STANDARD_SCHEDULE)
    assert r.status_code == 200


def _total_task_duration(data: dict) -> int:
    return sum(t["duration_minutes"] for t in data["tasks"])


# ============================================================
# Test 2: Normal Friday plan (no override)
# ============================================================

def test_normal_friday_plan_structure(client):
    _setup(client)
    r = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}")
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["day_name"] == "Friday"
    assert data["override_applied"] is False
    assert data["daily_override"] is None
    assert data["current_topic"] == "Hashing"
    assert data["revision_focus"] == "Arrays"
    assert data["available_minutes"] > 0
    assert _total_task_duration(data) <= data["available_minutes"]
    assert len(data["tasks"]) > 0
    assert len(data["recommended_problems"]) > 0
    # plan_reason must be a non-empty string
    assert data["plan_reason"]
    assert "SM-2" in data["revision_note"]


def test_normal_friday_budget_calculation(client):
    """
    Friday 09:00–14:00 = 300 class minutes (240 <= x < 360).
    Base budget = max(20, round(120 * 0.50)) = max(20, 60) = 60.
    No override → available_minutes = 60.
    """
    _setup(client)
    r = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}")
    assert r.status_code == 200
    assert r.json()["available_minutes"] == 60


def test_normal_friday_balanced_intensity(client):
    """
    Friday 09:00-14:00 = 300 class mins → budget = 60.
    60 < round(120 * 0.75) = 90  → intensity == "Balanced".
    """
    _setup(client)
    data = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}").json()
    assert data["plan_intensity"] == "Balanced"


# ============================================================
# Test 3: Internal exam override
# ============================================================

EXAM_OVERRIDE = {
    "situation": "Internal exam / Test",
    "extra_available_minutes": 0,
    "energy_level": "Low",
    "note": "Physics internal exam today",
}


def test_exam_override_plan(client):
    _setup(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{FRIDAY_DATE}",
        json=EXAM_OVERRIDE,
    )

    r = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}")
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["override_applied"] is True
    assert data["derived_workload"] == "High"
    assert data["plan_intensity"] == "Light"
    # Internal exam → budget = minimum_daily_minutes = 20
    assert data["available_minutes"] == 20
    assert _total_task_duration(data) <= data["available_minutes"]


def test_exam_override_easy_ranked_first(client):
    """Exam day → top-ranked problem must be Easy."""
    _setup(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{FRIDAY_DATE}",
        json=EXAM_OVERRIDE,
    )
    data = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}").json()
    problems = data["recommended_problems"]

    # The top-ranked problem must be Easy
    assert problems[0]["difficulty"] == "Easy"


# ============================================================
# Test 4: Free Saturday plan
# ============================================================

def test_free_saturday_plan(client):
    _setup(client)
    r = client.get(f"/api/users/demo-user/daily-plan/{SATURDAY_DATE}")
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["day_name"] == "Saturday"
    assert data["plan_intensity"] == "Deep"
    # Saturday is free → available = maximum_daily_minutes = 120
    assert data["available_minutes"] == 120
    assert _total_task_duration(data) <= data["available_minutes"]


# ============================================================
# Test 5: Competitive Programming + Prefix Sum on free day
# ============================================================

def test_competitive_programming_free_day_top_recommendation(client):
    _setup(client, profile=COMPETITIVE_PROFILE)
    r = client.get(f"/api/users/demo-user/daily-plan/{SATURDAY_DATE}")
    assert r.status_code == 200, r.text

    problems = r.json()["recommended_problems"]
    assert problems[0]["title"] == "Subarray Sum Equals K"


# ============================================================
# Test 6: Weekly schedule unchanged after override + plan
# ============================================================

def test_weekly_schedule_unchanged_after_daily_plan(client):
    _setup(client)
    client.put(
        f"/api/users/demo-user/daily-overrides/{FRIDAY_DATE}",
        json=EXAM_OVERRIDE,
    )
    # Generate the plan
    client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}")

    # Verify the original schedule is untouched
    r = client.get("/api/users/demo-user/weekly-schedule")
    assert r.status_code == 200
    days = r.json()["schedule"]["days"]
    saturday = next(d for d in days if d["day"] == "Saturday")
    assert saturday["is_free_day"] is True
    assert saturday["classes"] == []

    friday = next(d for d in days if d["day"] == "Friday")
    assert friday["is_free_day"] is False
    assert friday["classes"][0]["start_time"] == "09:00"
    assert friday["classes"][0]["end_time"] == "14:00"


# ============================================================
# Test 7: Missing profile / schedule returns 404
# ============================================================

def test_daily_plan_no_profile_returns_404(client):
    r = client.get(f"/api/users/ghost-user/daily-plan/{FRIDAY_DATE}")
    assert r.status_code == 404


def test_daily_plan_no_schedule_returns_404(client):
    client.put("/api/users/demo-user/profile", json=PLACEMENT_PROFILE)
    r = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}")
    assert r.status_code == 404


# ============================================================
# Test 8 & 9: Schedule validation — invalid class slots
# ============================================================

def _make_schedule_with_friday_classes(classes: list[dict]) -> dict:
    """Build a full 7-day schedule with custom Friday classes."""
    return {
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": []},
            {"day": "Tuesday",   "is_free_day": False, "classes": []},
            {"day": "Wednesday", "is_free_day": False, "classes": []},
            {"day": "Thursday",  "is_free_day": False, "classes": []},
            {"day": "Friday",    "is_free_day": False, "classes": classes},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
            {"day": "Sunday",    "is_free_day": True,  "classes": []},
        ]
    }


def test_schedule_rejects_end_time_before_start_time(client):
    """A slot where end_time < start_time must return 400."""
    schedule = _make_schedule_with_friday_classes(
        [{"title": "Bad Slot", "start_time": "14:00", "end_time": "09:00"}]
    )
    r = client.put("/api/users/demo-user/weekly-schedule", json=schedule)
    assert r.status_code == 400
    assert "end_time" in r.json()["detail"].lower() or "not later" in r.json()["detail"].lower()


def test_schedule_rejects_end_time_equal_to_start_time(client):
    """A zero-duration slot (start == end) must return 400."""
    schedule = _make_schedule_with_friday_classes(
        [{"title": "Zero Slot", "start_time": "10:00", "end_time": "10:00"}]
    )
    r = client.put("/api/users/demo-user/weekly-schedule", json=schedule)
    assert r.status_code == 400


def test_schedule_rejects_overlapping_classes(client):
    """Two overlapping slots on the same day must return 400."""
    schedule = _make_schedule_with_friday_classes(
        [
            {"title": "Lecture A", "start_time": "09:00", "end_time": "11:00"},
            {"title": "Lecture B", "start_time": "10:30", "end_time": "12:30"},
        ]
    )
    r = client.put("/api/users/demo-user/weekly-schedule", json=schedule)
    assert r.status_code == 400
    assert "overlap" in r.json()["detail"].lower()


def test_schedule_accepts_back_to_back_non_overlapping_classes(client):
    """Back-to-back slots (A ends at 11:00, B starts at 11:00) must pass."""
    schedule = _make_schedule_with_friday_classes(
        [
            {"title": "Morning", "start_time": "09:00", "end_time": "11:00"},
            {"title": "Afternoon", "start_time": "11:00", "end_time": "14:00"},
        ]
    )
    r = client.put("/api/users/demo-user/weekly-schedule", json=schedule)
    assert r.status_code == 200


# ============================================================
# Additional edge-case tests
# ============================================================

def test_task_durations_never_exceed_budget(client):
    """Property test: across several plan types, task sum ≤ available_minutes."""
    _setup(client)
    for date in [FRIDAY_DATE, SATURDAY_DATE]:
        data = client.get(f"/api/users/demo-user/daily-plan/{date}").json()
        assert _total_task_duration(data) <= data["available_minutes"], (
            f"Task total {_total_task_duration(data)} exceeded "
            f"budget {data['available_minutes']} for {date}"
        )


def test_rest_plan_has_zero_duration_task(client):
    """
    Force a Rest plan by sending extra_available_minutes = -240 on a
    day where base budget is the minimum (exam day = min_mins = 20).
    20 + (-240) clamped to 0 → Rest intensity.
    """
    _setup(client)
    # Exam day sets budget to min_mins (20), then -240 extra → clamp to 0
    rest_override = {
        "situation": "Internal exam / Test",
        "extra_available_minutes": -240,
        "energy_level": "Normal",
    }
    client.put(
        f"/api/users/demo-user/daily-overrides/{FRIDAY_DATE}",
        json=rest_override,
    )
    data = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}").json()
    assert data["plan_intensity"] == "Rest"
    assert data["available_minutes"] == 0
    assert data["tasks"][0]["task_type"] == "Recovery"
    assert _total_task_duration(data) == 0


def test_revision_note_is_honest(client):
    """revision_note must not claim SM-2 history already exists."""
    _setup(client)
    data = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}").json()
    note = data["revision_note"].lower()
    assert "sm-2" in note
    assert "next phase" in note or "will be integrated" in note


def test_plan_date_weekday_derived_correctly(client):
    """2026-05-22 is a Friday; 2026-05-23 is a Saturday."""
    _setup(client)
    fri = client.get(f"/api/users/demo-user/daily-plan/{FRIDAY_DATE}").json()
    sat = client.get(f"/api/users/demo-user/daily-plan/{SATURDAY_DATE}").json()
    assert fri["day_name"] == "Friday"
    assert sat["day_name"] == "Saturday"
