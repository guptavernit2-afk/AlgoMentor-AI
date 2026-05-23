"""
AlgoMentor AI — Live Database Verification for SM-2 Persistence.

This script manually verifies `PostgresRevisionRepository` by interacting
with the live Supabase instance defined in `backend/.env`.

It explicitly uses PostgresProfileRepository, PostgresScheduleRepository,
and PostgresRevisionRepository to:
  1. Write a parent student profile.
  2. Write a parent weekly schedule.
  3. Submit 3 SM-2 reviews for the same topic.
  4. Assert the final SM-2 state matches expectations.
  5. Assert the append-only history captured all 3 events.
  6. Call get_revision_queue and assert the topic is due.
  7. Call get_sm2_revision_focus to confirm Smart Daily Plan integration.

Run from the `backend/` directory:
    python -m scripts.smoke_test_sm2_persistence
"""

import os
from datetime import date as Date

# Force postgres mode for this script
os.environ["STORAGE_BACKEND"] = "postgres"

from app.config import get_settings
from app.models import StudentProfile, TopicReviewRequest, WeeklySchedule
from app.repositories.profile_repository import get_profile_repository
from app.repositories.revision_repository import get_revision_repository
from app.repositories.schedule_repository import get_schedule_repository
from app.services.sm2_service import (
    get_revision_queue,
    get_sm2_revision_focus,
    record_topic_review,
)

# ============================================================
# Test Data
# ============================================================

TEST_USER = "demo-user-sm2-db-test"
TOPIC = "Arrays"

PROFILE = {
    "name": "Vernit",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": [TOPIC],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}

SCHEDULE = {
    "days": [
        {"day": "Monday",    "is_free_day": False, "classes": [{"title": "College", "start_time": "09:00", "end_time": "16:00"}]},
        {"day": "Tuesday",   "is_free_day": False, "classes": [{"title": "College", "start_time": "09:00", "end_time": "13:00"}]},
        {"day": "Wednesday", "is_free_day": False, "classes": [{"title": "College", "start_time": "09:00", "end_time": "16:00"}]},
        {"day": "Thursday",  "is_free_day": False, "classes": [{"title": "College", "start_time": "10:00", "end_time": "15:00"}]},
        {"day": "Friday",    "is_free_day": False, "classes": [{"title": "College", "start_time": "09:00", "end_time": "14:00"}]},
        {"day": "Saturday",  "is_free_day": True,  "classes": []},
        {"day": "Sunday",    "is_free_day": True,  "classes": []},
    ]
}


def main():
    settings = get_settings()
    if settings.storage_backend != "postgres":
        print(f"Error: storage_backend must be 'postgres' (found '{settings.storage_backend}').")
        print("Check your backend/.env file.")
        return

    profile_repo = get_profile_repository()
    schedule_repo = get_schedule_repository()
    revision_repo = get_revision_repository()

    try:
        # 1. Profile
        print(f"\n[1/7] Saving profile for '{TEST_USER}' to Supabase ...")
        profile = StudentProfile.model_validate(PROFILE)
        profile_repo.save_profile(TEST_USER, profile)
        print("      Profile saved.")

        # 2. Schedule
        print(f"[2/7] Saving weekly schedule for '{TEST_USER}' to Supabase ...")
        schedule_model = WeeklySchedule.model_validate(SCHEDULE)
        schedule_repo.save_schedule(TEST_USER, schedule_model)
        print("      Schedule saved (7 rows).")

        # 3. SM-2 Reviews
        print(f"[3/7] Submitting 3 SM-2 reviews for '{TOPIC}' to Supabase ...")
        reviews = [
            TopicReviewRequest(topic=TOPIC, quality=5, reviewed_on=Date(2026, 5, 22)),
            TopicReviewRequest(topic=TOPIC, quality=5, reviewed_on=Date(2026, 5, 23)),
            TopicReviewRequest(topic=TOPIC, quality=5, reviewed_on=Date(2026, 5, 29)),
        ]
        
        final_state = None
        for req in reviews:
            final_state = record_topic_review(TEST_USER, profile, req)
        print("      Reviews recorded atomically.")

        # 4. Verify Current State
        print(f"[4/7] Verifying current SM-2 state from Supabase ...")
        state = revision_repo.get_state(TEST_USER, TOPIC)
        assert state is not None
        assert state.repetitions == 3
        assert state.interval_days == 17
        assert state.easiness_factor == 2.8
        assert state.last_quality == 5
        assert state.last_reviewed_on == Date(2026, 5, 29)
        assert state.next_review_date == Date(2026, 6, 15)
        assert state.total_reviews == 3
        print("      State verification passed.")

        # 5. Verify History
        print(f"[5/7] Verifying append-only history from Supabase ...")
        history = revision_repo.list_history(TEST_USER)
        topic_history = [r for r in history if r.topic == TOPIC]
        assert len(topic_history) == 3
        assert topic_history[0].reviewed_on == Date(2026, 5, 22)
        assert topic_history[1].reviewed_on == Date(2026, 5, 23)
        assert topic_history[2].reviewed_on == Date(2026, 5, 29)
        print("      History verification passed (3 records).")

        # 6. Verify Queue
        print(f"[6/7] Verifying Revision Queue as of 2026-06-15 ...")
        queue = get_revision_queue(TEST_USER, profile, as_of_date=Date(2026, 6, 15))
        assert len(queue.due_topics) == 1
        assert queue.due_topics[0].topic == TOPIC
        print("      Revision queue returned due topic correctly.")

        # 7. Verify Daily Plan Integration
        print(f"[7/7] Verifying Smart Daily Plan integration as of 2026-06-15 ...")
        focus, note = get_sm2_revision_focus(TEST_USER, plan_date=Date(2026, 6, 15))
        assert focus == TOPIC
        assert "SM-2 due queue" in note
        print("      Smart Daily Plan correctly selected the persisted due topic.")

        # --- Success ---
        print("\n============================================================")
        print("All assertions passed.")
        print("============================================================\n")

        print("SM-2 persistence verified successfully for demo-user-sm2-db-test.")
        print("Arrays state persisted: 3 reviews, next revision date 2026-06-15.")
        print("Smart Daily Plan correctly selected the persisted due topic.\n")

        print("The following rows are now visible in Supabase Table Editor:")
        print(f"  student_profiles      -> {TEST_USER}  (1 row)")
        print(f"  weekly_schedules      -> {TEST_USER}  (7 rows)")
        print(f"  topic_revision_states -> {TEST_USER} / {TOPIC} (1 row)")
        print(f"  topic_review_history  -> {TEST_USER} / {TOPIC} (3 rows)")
        
        print("\nDELETE INSTRUCTIONS:")
        print(f"  Delete only the student_profiles row for {TEST_USER}.")
        print("  The ON DELETE CASCADE policy will automatically remove all")
        print("  schedule, state, and history rows for this user.")

    except AssertionError as e:
        print(f"\n[!] Assertion Failed: {e}")
    except Exception as e:
        print(f"\n[!] Unexpected Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
