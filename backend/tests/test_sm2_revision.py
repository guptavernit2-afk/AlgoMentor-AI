"""
AlgoMentor AI — tests for the SM-2 Revision History engine.

Covers:
  A. First review state
  B. Second review state
  C. Third review (uses previous EF for interval)
  D. Failed recall resets interval
  E. EF lower bound enforced
  F. Topic validation
  G. Revision queue (due / upcoming / untracked)
  H. Daily Plan picks SM-2 due topic
  I. Daily Plan with states but none due
  J. Regression: existing 38 tests unaffected (run all together)

Run from backend/:
    pytest tests/test_sm2_revision.py -v
"""

import math
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import clear_all_stores


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def reset_stores():
    clear_all_stores()
    yield
    clear_all_stores()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ============================================================
# Shared test data
# ============================================================

PROFILE = {
    "name": "Vernit",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}

SCHEDULE = {
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


def _setup(client: TestClient) -> None:
    """Persist demo profile + schedule."""
    r = client.put("/api/users/demo-user/profile", json=PROFILE)
    assert r.status_code == 200
    r = client.put("/api/users/demo-user/weekly-schedule", json=SCHEDULE)
    assert r.status_code == 200


def _review(client: TestClient, topic: str, quality: int, reviewed_on: str) -> dict:
    r = client.post(
        "/api/users/demo-user/revision-reviews",
        json={"topic": topic, "quality": quality, "reviewed_on": reviewed_on},
    )
    assert r.status_code == 200, r.text
    return r.json()["state"]


# ============================================================
# A. First successful review (quality 5, first-ever)
# ============================================================

def test_first_review_quality_5(client):
    """
    First review: repetitions=0, quality=5.
    Expected: repetitions=1, interval=1, EF=2.6, next=2026-05-23.
    """
    _setup(client)
    state = _review(client, "Arrays", 5, "2026-05-22")

    assert state["repetitions"] == 1
    assert state["interval_days"] == 1
    assert state["easiness_factor"] == 2.6
    assert state["next_review_date"] == "2026-05-23"
    assert state["last_quality"] == 5
    assert state["total_reviews"] == 1


def test_first_review_response_message(client):
    _setup(client)
    r = client.post(
        "/api/users/demo-user/revision-reviews",
        json={"topic": "Arrays", "quality": 5, "reviewed_on": "2026-05-22"},
    )
    assert r.status_code == 200
    assert r.json()["message"] == (
        "Topic review recorded and next revision scheduled using SM-2."
    )


# ============================================================
# B. Second successful review (quality 5)
# ============================================================

def test_second_review_quality_5(client):
    """
    Second review: repetitions=1, quality=5.
    Expected: repetitions=2, interval=6, EF=2.7, next=2026-05-29.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")   # first
    state = _review(client, "Arrays", 5, "2026-05-23")  # second

    assert state["repetitions"] == 2
    assert state["interval_days"] == 6
    assert state["easiness_factor"] == 2.7
    assert state["next_review_date"] == "2026-05-29"
    assert state["total_reviews"] == 2


# ============================================================
# C. Third successful review uses previous EF for interval
# ============================================================

def test_third_review_uses_previous_ef(client):
    """
    Third review: repetitions=2, prev_interval=6, prev_EF=2.7, quality=5.
    new_interval = ceil(6 * 2.7) = ceil(16.2) = 17.
    new_EF = 2.7 + 0.1 - 0 = 2.8.
    next = 2026-05-29 + 17 = 2026-06-15.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")
    _review(client, "Arrays", 5, "2026-05-23")
    state = _review(client, "Arrays", 5, "2026-05-29")

    expected_interval = math.ceil(6 * 2.7)  # 17
    assert state["repetitions"] == 3
    assert state["interval_days"] == expected_interval
    assert state["easiness_factor"] == 2.8
    assert state["next_review_date"] == "2026-06-15"


# ============================================================
# D. Failed recall resets interval
# ============================================================

def test_failed_recall_resets_interval(client):
    """
    After two successful reviews, submitting quality=2 must reset:
    repetitions=0, interval_days=1, next=reviewed_on+1.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")
    _review(client, "Arrays", 5, "2026-05-23")
    state = _review(client, "Arrays", 2, "2026-05-29")  # fail

    assert state["repetitions"] == 0
    assert state["interval_days"] == 1
    assert state["next_review_date"] == "2026-05-30"
    assert state["easiness_factor"] >= 1.3


def test_quality_boundary_2_is_fail_3_is_pass(client):
    """quality < 3 resets; quality >= 3 advances."""
    _setup(client)
    # quality=2 → fail
    s2 = _review(client, "Arrays", 2, "2026-05-22")
    assert s2["repetitions"] == 0

    clear_all_stores()
    _setup(client)
    # quality=3 → pass
    s3 = _review(client, "Arrays", 3, "2026-05-22")
    assert s3["repetitions"] == 1


# ============================================================
# E. EF lower bound
# ============================================================

def test_ef_never_falls_below_1_3(client):
    """Repeated quality=0 reviews must keep EF >= 1.3."""
    _setup(client)
    ef_values = []
    # Perform 10 terrible reviews
    for i in range(10):
        reviewed_on = date(2026, 5, 22) + timedelta(days=i)
        state = _review(client, "Arrays", 0, reviewed_on.isoformat())
        ef_values.append(state["easiness_factor"])

    assert all(ef >= 1.3 for ef in ef_values), (
        f"EF dipped below 1.3: {ef_values}"
    )


def test_ef_formula_quality_4(client):
    """
    quality=4: new_EF = 2.5 + 0.1 - (5-4)*(0.08+(5-4)*0.02)
                      = 2.5 + 0.1 - 1*0.10 = 2.5 → 2.5.
    """
    _setup(client)
    state = _review(client, "Arrays", 4, "2026-05-22")
    assert state["easiness_factor"] == 2.5


def test_ef_formula_quality_3(client):
    """
    quality=3: new_EF = 2.5 + 0.1 - (5-3)*(0.08+(5-3)*0.02)
                      = 2.5 + 0.1 - 2*(0.08+0.04) = 2.5 + 0.1 - 0.24 = 2.36.
    """
    _setup(client)
    state = _review(client, "Arrays", 3, "2026-05-22")
    assert state["easiness_factor"] == 2.36


# ============================================================
# F. Topic validation
# ============================================================

def test_unknown_topic_returns_400(client):
    """Reviewing 'Graphs' when profile has only Arrays + Hashing must fail."""
    _setup(client)
    r = client.post(
        "/api/users/demo-user/revision-reviews",
        json={"topic": "Graphs", "quality": 4, "reviewed_on": "2026-05-22"},
    )
    assert r.status_code == 400
    assert "completed topics" in r.json()["detail"].lower()


def test_current_topic_is_valid(client):
    """The student's current_topic ('Hashing') should be reviewable."""
    _setup(client)
    state = _review(client, "Hashing", 4, "2026-05-22")
    assert state["topic"] == "Hashing"


def test_topic_match_is_case_insensitive(client):
    """'arrays' and 'ARRAYS' should both resolve to 'Arrays'."""
    _setup(client)
    state = _review(client, "arrays", 4, "2026-05-22")
    assert state["topic"] == "Arrays"


def test_review_without_profile_returns_404(client):
    r = client.post(
        "/api/users/ghost-user/revision-reviews",
        json={"topic": "Arrays", "quality": 4, "reviewed_on": "2026-05-22"},
    )
    assert r.status_code == 404


# ============================================================
# G. Revision queue
# ============================================================

def test_revision_queue_splits_due_and_upcoming(client):
    """
    Review Arrays on 2026-05-22 → next review 2026-05-23.
    Query as_of_date=2026-05-23 → Arrays should appear in due_topics.
    Query as_of_date=2026-05-22 → Arrays should appear in upcoming_topics.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")  # next=2026-05-23

    # Due query
    r = client.get("/api/users/demo-user/revision-queue/2026-05-23")
    assert r.status_code == 200
    data = r.json()
    due = data["due_topics"]
    assert len(due) == 1
    assert due[0]["topic"] == "Arrays"
    assert due[0]["is_due"] is True
    assert due[0]["days_overdue"] == 0

    # Upcoming query (one day before due)
    r2 = client.get("/api/users/demo-user/revision-queue/2026-05-22")
    data2 = r2.json()
    assert len(data2["due_topics"]) == 0
    assert len(data2["upcoming_topics"]) == 1


def test_revision_queue_message_when_due(client):
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")
    r = client.get("/api/users/demo-user/revision-queue/2026-05-23")
    assert r.json()["message"] == "Revision topics are due today."


def test_revision_queue_message_when_not_due(client):
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")
    r = client.get("/api/users/demo-user/revision-queue/2026-05-22")
    assert r.json()["message"] == "No tracked topics are due today."


def test_revision_queue_untracked_completed_topics(client):
    """Arrays is completed but has no SM-2 state yet → should appear in untracked."""
    _setup(client)
    r = client.get("/api/users/demo-user/revision-queue/2026-05-22")
    data = r.json()
    assert "Arrays" in data["untracked_completed_topics"]


def test_revision_queue_sorted_most_overdue_first(client):
    """
    Setup two topics with different due dates.
    The most overdue one should be first in due_topics.
    """
    # Extend profile to include a second completed topic
    extended_profile = {**PROFILE, "completed_topics": ["Arrays", "Binary Search"]}
    client.put("/api/users/demo-user/profile", json=extended_profile)
    client.put("/api/users/demo-user/weekly-schedule", json=SCHEDULE)

    # Arrays: reviewed 2026-05-10, quality 5 → next 2026-05-11
    _review(client, "Arrays", 5, "2026-05-10")
    # Binary Search: reviewed 2026-05-20, quality 5 → next 2026-05-21
    _review(client, "Binary Search", 5, "2026-05-20")

    # Query on 2026-05-23: both are due; Arrays is more overdue
    r = client.get("/api/users/demo-user/revision-queue/2026-05-23")
    data = r.json()
    assert len(data["due_topics"]) == 2
    assert data["due_topics"][0]["topic"] == "Arrays"  # most overdue
    assert data["due_topics"][1]["topic"] == "Binary Search"


def test_revision_queue_no_profile_returns_404(client):
    r = client.get("/api/users/ghost-user/revision-queue/2026-05-22")
    assert r.status_code == 404


# ============================================================
# H. Daily Plan chooses due SM-2 topic
# ============================================================

def test_daily_plan_uses_sm2_due_topic(client):
    """
    Record a review of Arrays on 2026-05-22 (first review → next=2026-05-23).
    GET daily plan for 2026-05-23.
    revision_focus must be 'Arrays'; revision_note must mention SM-2 due queue.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")  # next_review = 2026-05-23

    # Plan for the due date
    r = client.get("/api/users/demo-user/daily-plan/2026-05-23")
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["revision_focus"] == "Arrays"
    assert "SM-2" in data["revision_note"]
    assert "due" in data["revision_note"].lower() or "2026-05-23" in data["revision_note"]

    # Task durations must still not exceed budget
    total_duration = sum(t["duration_minutes"] for t in data["tasks"])
    assert total_duration <= data["available_minutes"]


def test_daily_plan_sm2_overdue_topic(client):
    """
    Arrays due 2026-05-23 but we check on 2026-05-25 (2 days overdue).
    Plan should still pick Arrays.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")  # next=2026-05-23

    r = client.get("/api/users/demo-user/daily-plan/2026-05-25")
    data = r.json()
    assert data["revision_focus"] == "Arrays"
    assert "2026-05-23" in data["revision_note"]  # due date stated


# ============================================================
# I. Daily Plan with tracked topics but none due
# ============================================================

def test_daily_plan_no_due_topic_revision_focus_is_none(client):
    """
    Record Arrays review on 2026-05-22 → next review 2026-05-23.
    GET plan for 2026-05-22 (before due date).
    No SM-2 topic is due → revision_focus must be None.
    revision_note must NOT claim it is due.
    """
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")

    # Plan for the same day as review (not yet due)
    r = client.get("/api/users/demo-user/daily-plan/2026-05-22")
    assert r.status_code == 200, r.text
    data = r.json()

    assert data["revision_focus"] is None
    note = data["revision_note"].lower()
    assert "due" not in note or "no" in note or "2026-05-23" in data["revision_note"]


def test_daily_plan_no_sm2_history_uses_fallback(client):
    """
    With no SM-2 review records at all, daily plan falls back to
    revision_focus = first completed topic and the honest SM-2 note.
    """
    _setup(client)
    r = client.get("/api/users/demo-user/daily-plan/2026-05-22")
    assert r.status_code == 200
    data = r.json()

    # Should use profile fallback
    assert data["revision_focus"] == "Arrays"
    assert "SM-2" in data["revision_note"]
    assert "next phase" in data["revision_note"].lower() or "completed topics" in data["revision_note"].lower()


# ============================================================
# Revision history endpoint
# ============================================================

def test_revision_history_returns_records(client):
    _setup(client)
    _review(client, "Arrays", 5, "2026-05-22")
    _review(client, "Arrays", 4, "2026-05-23")

    r = client.get("/api/users/demo-user/revision-history")
    assert r.status_code == 200
    data = r.json()
    assert data["total_records"] == 2
    assert data["history"][0]["quality"] == 5
    assert data["history"][1]["quality"] == 4


def test_revision_history_no_profile_returns_404(client):
    r = client.get("/api/users/ghost-user/revision-history")
    assert r.status_code == 404


# ============================================================
# Edge cases
# ============================================================

def test_review_quality_out_of_range_returns_422(client):
    _setup(client)
    r = client.post(
        "/api/users/demo-user/revision-reviews",
        json={"topic": "Arrays", "quality": 6, "reviewed_on": "2026-05-22"},
    )
    assert r.status_code == 422  # Pydantic validation error


def test_multiple_topics_tracked_independently(client):
    """Hashing and Arrays are tracked separately."""
    _setup(client)
    s_arrays  = _review(client, "Arrays",  5, "2026-05-22")
    s_hashing = _review(client, "Hashing", 4, "2026-05-22")

    assert s_arrays["topic"]  == "Arrays"
    assert s_hashing["topic"] == "Hashing"
    # Both are independent: Arrays interval=1, Hashing interval=1
    assert s_arrays["repetitions"]  == 1
    assert s_hashing["repetitions"] == 1
