"""
AlgoMentor AI — Manual profile persistence smoke test.

Verifies that the Student Profile API correctly persists data in Supabase
when STORAGE_BACKEND=postgres is set in backend/.env.

Run from the backend/ folder:
    python -m scripts.smoke_test_profile_persistence

Prerequisites:
  1. Create backend/.env from backend/.env.example.
  2. Fill in the real Supabase Session Pooler credentials.
  3. Set STORAGE_BACKEND=postgres in backend/.env.
  4. Ensure the public.student_profiles table exists (run schema.sql first).

This script writes one row with user_id='demo-user-db-test'.
It does NOT delete the row automatically — confirm it visually in
Supabase Table Editor, then delete it manually.

NEVER commit backend/.env.
"""

import sys
import os

# Allow imports from backend/ root when invoked as `python -m scripts.smoke_test_...`
# This is a no-op when using -m (Python already adds the CWD), but keeps
# direct invocation (`python scripts/smoke_test_profile_persistence.py`) working too.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings


TEST_USER_ID = "demo-user-db-test"

TEST_PROFILE = {
    "name": "Vernit",
    "goal": "Placement Prep",
    "current_topic": "Hashing",
    "completed_topics": ["Arrays"],
    "weak_concepts": ["Prefix Sum"],
    "preferred_study_time": "Evening",
    "minimum_daily_minutes": 20,
    "maximum_daily_minutes": 120,
}


def main() -> None:
    settings = get_settings()

    if settings.storage_backend != "postgres":
        print(
            "Storage backend is set to 'memory'. "
            "Set STORAGE_BACKEND=postgres in backend/.env to test Supabase persistence."
        )
        sys.exit(0)

    # Lazy imports so that misconfiguration errors are reported cleanly.
    from app.models import StudentProfile
    from app.repositories.profile_repository import (
        get_profile_repository,
        PostgresProfileRepository,
    )

    repo = get_profile_repository()
    if not isinstance(repo, PostgresProfileRepository):
        print("Unexpected: repository is not PostgresProfileRepository. Check config.")
        sys.exit(1)

    profile = StudentProfile(**TEST_PROFILE)

    # ---- Save ----
    print(f"Saving profile for '{TEST_USER_ID}' to Supabase …")
    try:
        repo.save_profile(TEST_USER_ID, profile)
    except RuntimeError as exc:
        print(f"Save failed: {exc}")
        sys.exit(1)

    # ---- Read back ----
    print(f"Reading profile for '{TEST_USER_ID}' from Supabase …")
    try:
        fetched = repo.get_profile(TEST_USER_ID)
    except RuntimeError as exc:
        print(f"Read failed: {exc}")
        sys.exit(1)

    if fetched is None:
        print(
            f"ERROR: Profile for '{TEST_USER_ID}' was not found after saving. "
            "Check Supabase RLS and connection settings."
        )
        sys.exit(1)

    # ---- Verify fields ----
    assert fetched.name == profile.name, f"name mismatch: {fetched.name!r}"
    assert fetched.goal == profile.goal, f"goal mismatch: {fetched.goal!r}"
    assert fetched.current_topic == profile.current_topic
    assert fetched.completed_topics == profile.completed_topics
    assert fetched.weak_concepts == profile.weak_concepts
    assert fetched.preferred_study_time == profile.preferred_study_time
    assert fetched.minimum_daily_minutes == profile.minimum_daily_minutes
    assert fetched.maximum_daily_minutes == profile.maximum_daily_minutes

    print(
        f"Student profile persistence verified successfully for {TEST_USER_ID}.\n"
        "The row is now visible in Supabase Table Editor -> student_profiles.\n"
        "Delete it manually after visual confirmation."
    )


if __name__ == "__main__":
    main()
