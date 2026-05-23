"""
AlgoMentor AI — Manual smoke test for Daily Override Supabase persistence.

PURPOSE:
    Verify that PostgresDailyOverrideRepository correctly saves and retrieves
    a daily override from public.daily_overrides in Supabase, and that the
    Smart Daily Plan service reads the persisted override correctly.

    This script is NOT part of the automated test suite. Run it manually
    after confirming that backend/.env sets STORAGE_BACKEND=postgres.

SAFE TEST DATA:
    user_id: demo-user-override-db-test
    override_date: 2026-05-22 (a Friday)

WHAT THIS SCRIPT DOES:
    1. Saves a student profile (required by FK on weekly_schedules and daily_overrides).
    2. Saves a valid seven-day weekly schedule.
    3. Saves a daily override: Internal exam / Test on 2026-05-22.
    4. Reads the override back from Supabase and asserts values.
    5. Generates the Smart Daily Plan for 2026-05-22 via the API service layer
       and asserts the override was applied correctly.
    6. Prints only safe, credential-free output.

ROWS WRITTEN (do NOT delete automatically — verify visually first):
    - public.student_profiles  (1 row)  → demo-user-override-db-test
    - public.weekly_schedules  (7 rows) → one per weekday
    - public.daily_overrides   (1 row)  → 2026-05-22

DELETE STRATEGY:
    Delete only the parent student_profiles row for demo-user-override-db-test
    in the Supabase Table Editor. The ON DELETE CASCADE policy on weekly_schedules
    and daily_overrides will automatically remove the related rows.

    Do NOT delete rows automatically in this script.

RUN FROM backend/:
    python -m scripts.smoke_test_daily_override_persistence
"""

from datetime import date

TEST_USER_ID  = "demo-user-override-db-test"
OVERRIDE_DATE = date(2026, 5, 22)          # Friday


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
    from app.repositories.daily_override_repository import PostgresDailyOverrideRepository
    from app.models import StudentProfile, WeeklySchedule, DailyOverride

    profile_repo  = PostgresProfileRepository()
    schedule_repo = PostgresScheduleRepository()
    override_repo = PostgresDailyOverrideRepository()

    # ----------------------------------------------------------------
    # Step 1: Save a student profile
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

    print(f"[1/5] Saving profile for '{TEST_USER_ID}' to Supabase ...")
    profile_repo.save_profile(TEST_USER_ID, profile)
    print("      Profile saved.")

    # ----------------------------------------------------------------
    # Step 2: Save a seven-day weekly schedule
    # ----------------------------------------------------------------
    schedule = WeeklySchedule(**{
        "days": [
            {"day": "Monday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
            {"day": "Tuesday",   "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "13:00"}]},
            {"day": "Wednesday", "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "16:00"}]},
            {"day": "Thursday",  "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "10:00", "end_time": "15:00"}]},
            {"day": "Friday",    "is_free_day": False, "classes": [{"title": "College Classes", "start_time": "09:00", "end_time": "14:00"}]},
            {"day": "Saturday",  "is_free_day": True,  "classes": []},
            {"day": "Sunday",    "is_free_day": True,  "classes": []},
        ]
    })

    print(f"[2/5] Saving weekly schedule for '{TEST_USER_ID}' to Supabase ...")
    schedule_repo.save_schedule(TEST_USER_ID, schedule)
    print("      Schedule saved (7 rows).")

    # ----------------------------------------------------------------
    # Step 3: Save a daily override
    # ----------------------------------------------------------------
    override = DailyOverride(
        situation="Internal exam / Test",
        extra_available_minutes=0,
        energy_level="Low",
        note="Physics internal exam today",
    )

    print(f"[3/5] Saving daily override for {OVERRIDE_DATE} to Supabase ...")
    override_repo.save_override(TEST_USER_ID, OVERRIDE_DATE, override)
    print("      Daily override saved.")

    # ----------------------------------------------------------------
    # Step 4: Read override back and assert values
    # ----------------------------------------------------------------
    print(f"[4/5] Reading daily override for {OVERRIDE_DATE} from Supabase ...")
    fetched = override_repo.get_override(TEST_USER_ID, OVERRIDE_DATE)

    assert fetched is not None, "get_override returned None — no row found in Supabase."
    assert fetched.situation == "Internal exam / Test", (
        f"situation mismatch: expected 'Internal exam / Test', got '{fetched.situation}'."
    )
    assert fetched.extra_available_minutes == 0, (
        f"extra_available_minutes mismatch: expected 0, got {fetched.extra_available_minutes}."
    )
    assert fetched.energy_level == "Low", (
        f"energy_level mismatch: expected 'Low', got '{fetched.energy_level}'."
    )
    assert fetched.note == "Physics internal exam today", (
        f"note mismatch: expected 'Physics internal exam today', got '{fetched.note}'."
    )
    print("      Override values verified.")
    print("      Daily override persistence verified successfully for demo-user-override-db-test.")

    # ----------------------------------------------------------------
    # Step 5: Generate a Smart Daily Plan via service layer
    # ----------------------------------------------------------------
    print(f"[5/5] Generating Smart Daily Plan for {OVERRIDE_DATE} in postgres mode ...")

    from app.services.daily_plan_service import build_daily_plan
    from app.services.daily_override_service import get_optional_daily_override
    from app.repositories.schedule_repository import PostgresScheduleRepository

    # Re-use already-saved data via direct service/repo calls
    fetched_profile  = profile_repo.get_profile(TEST_USER_ID)
    fetched_schedule = schedule_repo.get_schedule(TEST_USER_ID)
    fetched_override = get_optional_daily_override(TEST_USER_ID, OVERRIDE_DATE)

    assert fetched_profile  is not None, "Profile not found in Supabase."
    assert fetched_schedule is not None, "Weekly schedule not found in Supabase."

    # 2026-05-22 is a Friday (weekday index 4)
    day_name = "Friday"
    day_schedule = next(
        (d for d in fetched_schedule.days if d.day == day_name), None
    )
    assert day_schedule is not None, f"{day_name} not found in weekly schedule."

    plan = build_daily_plan(
        user_id=TEST_USER_ID,
        plan_date=OVERRIDE_DATE,
        profile=fetched_profile,
        day_schedule=day_schedule,
        override=fetched_override,
    )

    # Verify the override was correctly applied to the plan
    assert plan.override_applied is True, (
        f"override_applied should be True, got {plan.override_applied}."
    )
    assert plan.derived_workload == "High", (
        f"derived_workload should be 'High', got '{plan.derived_workload}'."
    )
    assert plan.plan_intensity == "Light", (
        f"plan_intensity should be 'Light', got '{plan.plan_intensity}'."
    )
    assert plan.available_minutes == 20, (
        f"available_minutes should be 20 (minimum_daily_minutes), got {plan.available_minutes}."
    )

    print("      Smart Daily Plan generated successfully.")
    print("      Smart Daily Plan correctly applied the persisted Internal exam override.")

    # ----------------------------------------------------------------
    # Verify weekly schedule was not modified
    # ----------------------------------------------------------------
    re_fetched_schedule = schedule_repo.get_schedule(TEST_USER_ID)
    assert re_fetched_schedule is not None
    friday = next(d for d in re_fetched_schedule.days if d.day == "Friday")
    assert not friday.is_free_day, "Friday should still be a college day — timetable unchanged."
    assert friday.classes[0].start_time == "09:00"

    # ----------------------------------------------------------------
    # Safe summary output
    # ----------------------------------------------------------------
    print()
    print("=" * 60)
    print("All assertions passed.")
    print("=" * 60)
    print()
    print(f"The following rows are now visible in Supabase Table Editor:")
    print(f"  student_profiles  -> {TEST_USER_ID}  (1 row)")
    print(f"  weekly_schedules  -> {TEST_USER_ID}  (7 rows, one per weekday)")
    print(f"  daily_overrides   -> {TEST_USER_ID}  (1 row, date: {OVERRIDE_DATE})")
    print()
    print("DELETE INSTRUCTIONS:")
    print("  Delete only the student_profiles row for demo-user-override-db-test.")
    print("  The ON DELETE CASCADE will automatically remove weekly_schedules")
    print("  and daily_overrides rows for this user.")


if __name__ == "__main__":
    main()
