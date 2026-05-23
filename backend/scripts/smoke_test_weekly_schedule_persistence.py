"""
AlgoMentor AI — Manual smoke test for Weekly Schedule Supabase persistence.

PURPOSE:
    Verify that PostgresScheduleRepository correctly saves and retrieves
    a seven-day weekly schedule from public.weekly_schedules in Supabase.

    This script is NOT part of the automated test suite. Run it manually
    after confirming that backend/.env sets STORAGE_BACKEND=postgres.

SAFE TEST DATA:
    user_id: demo-user-schedule-db-test
    (a dedicated test identifier — never a real user account)

WHAT THIS SCRIPT DOES:
    1. Saves a student profile for the test user (required by FK constraint).
    2. Saves a valid seven-day weekly schedule for the test user.
    3. Reads the schedule back from Supabase.
    4. Asserts correctness of the returned data.
    5. Prints a safe success message (never prints credentials).

ROWS WRITTEN:
    - public.student_profiles  (1 row)  → demo-user-schedule-db-test
    - public.weekly_schedules  (7 rows) → one per weekday

DELETE MANUALLY:
    After visual confirmation in Supabase Table Editor, delete both the
    profile row and all seven schedule rows manually.
    The script does NOT delete rows automatically.

RUN FROM backend/:
    python -m scripts.smoke_test_weekly_schedule_persistence
"""

TEST_USER_ID = "demo-user-schedule-db-test"


def main() -> None:
    # ----------------------------------------------------------------
    # Guard: refuse to run in memory mode
    # ----------------------------------------------------------------
    from app.config import get_settings
    settings = get_settings()

    if settings.storage_backend != "postgres":
        print(
            "SKIP: STORAGE_BACKEND is not 'postgres'. "
            "Set STORAGE_BACKEND=postgres in backend/.env and re-run."
        )
        return

    # ----------------------------------------------------------------
    # Import repositories (after confirming postgres mode)
    # ----------------------------------------------------------------
    from app.repositories.profile_repository import PostgresProfileRepository
    from app.repositories.schedule_repository import PostgresScheduleRepository
    from app.models import StudentProfile, WeeklySchedule

    profile_repo = PostgresProfileRepository()
    schedule_repo = PostgresScheduleRepository()

    # ----------------------------------------------------------------
    # Step 1: Save a student profile (required by FK constraint)
    # ----------------------------------------------------------------
    profile = StudentProfile(
        name="Vernit",
        goal="Placement Prep",
        current_topic="Hashing",
        completed_topics=["Arrays"],
        weak_concepts=["Prefix Sum"],
        preferred_study_time="Evening",
        minimum_daily_minutes=20,
        maximum_daily_minutes=120,
    )

    print(f"Saving profile for '{TEST_USER_ID}' to Supabase ...")
    profile_repo.save_profile(TEST_USER_ID, profile)
    print("  Profile saved.")

    # ----------------------------------------------------------------
    # Step 2: Save a seven-day weekly schedule
    # ----------------------------------------------------------------
    schedule_data = {
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
    schedule = WeeklySchedule(**schedule_data)

    print(f"Saving weekly schedule (7 days) for '{TEST_USER_ID}' to Supabase ...")
    schedule_repo.save_schedule(TEST_USER_ID, schedule)
    print("  Schedule saved.")

    # ----------------------------------------------------------------
    # Step 3: Read back from Supabase
    # ----------------------------------------------------------------
    print(f"Reading weekly schedule for '{TEST_USER_ID}' from Supabase ...")
    fetched = schedule_repo.get_schedule(TEST_USER_ID)
    print("  Schedule retrieved.")

    # ----------------------------------------------------------------
    # Step 4: Assertions
    # ----------------------------------------------------------------
    assert fetched is not None, "get_schedule returned None — no rows found in Supabase."
    assert len(fetched.days) == 7, (
        f"Expected 7 days, got {len(fetched.days)}."
    )

    # Monday: one class 09:00-16:00
    monday = next((d for d in fetched.days if d.day == "Monday"), None)
    assert monday is not None, "Monday not found in returned schedule."
    assert not monday.is_free_day, "Monday should not be a free day."
    assert len(monday.classes) == 1, f"Monday should have 1 class, got {len(monday.classes)}."
    assert monday.classes[0].start_time == "09:00", (
        f"Monday class start_time should be 09:00, got {monday.classes[0].start_time}."
    )
    assert monday.classes[0].end_time == "16:00", (
        f"Monday class end_time should be 16:00, got {monday.classes[0].end_time}."
    )

    # Saturday: free day, no classes
    saturday = next((d for d in fetched.days if d.day == "Saturday"), None)
    assert saturday is not None, "Saturday not found in returned schedule."
    assert saturday.is_free_day, "Saturday should be a free day."
    assert saturday.classes == [], f"Saturday should have no classes, got {saturday.classes}."

    # Sunday: free day, no classes
    sunday = next((d for d in fetched.days if d.day == "Sunday"), None)
    assert sunday is not None, "Sunday not found in returned schedule."
    assert sunday.is_free_day, "Sunday should be a free day."
    assert sunday.classes == [], f"Sunday should have no classes, got {sunday.classes}."

    # ----------------------------------------------------------------
    # Step 5: Success
    # ----------------------------------------------------------------
    print()
    print(f"Weekly schedule persistence verified successfully for {TEST_USER_ID}.")
    print("The following rows are now visible in Supabase Table Editor:")
    print(f"  student_profiles  -> {TEST_USER_ID}  (1 row)")
    print(f"  weekly_schedules  -> {TEST_USER_ID}  (7 rows, one per weekday)")
    print("Delete them manually after visual confirmation.")


if __name__ == "__main__":
    main()
