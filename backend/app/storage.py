"""
AlgoMentor AI — in-memory storage.

Houses the five in-memory dictionaries that act as a temporary data
layer until Supabase persistence is added.  Also exports the two
require_* helpers so routers never import from each other.
"""

from datetime import date as Date

from fastapi import HTTPException

from app.models import (
    DailyOverride,
    StudentProfile,
    TopicReviewRecord,
    TopicRevisionState,
    WeeklySchedule,
)


# ============================================================
# In-Memory Stores
# Later these will be replaced by Supabase tables.
# ============================================================

PROFILE_STORE: dict[str, StudentProfile] = {}
SCHEDULE_STORE: dict[str, WeeklySchedule] = {}
DAILY_OVERRIDE_STORE: dict[tuple[str, Date], DailyOverride] = {}

# Key: (user_id, normalised_topic_name)
REVISION_STATE_STORE: dict[tuple[str, str], TopicRevisionState] = {}

# Key: user_id → list of all review records in chronological order
REVISION_HISTORY_STORE: dict[str, list[TopicReviewRecord]] = {}


# ============================================================
# Store helpers
# ============================================================

def clear_all_stores() -> None:
    """
    Reset every in-memory store to empty.

    Called from the test suite between test cases so that state
    from one test never bleeds into another.
    """
    PROFILE_STORE.clear()
    SCHEDULE_STORE.clear()
    DAILY_OVERRIDE_STORE.clear()
    REVISION_STATE_STORE.clear()
    REVISION_HISTORY_STORE.clear()


# ============================================================
# Shared guard helpers used by multiple routers
# ============================================================

def require_profile(user_id: str) -> StudentProfile:
    """Return saved profile or raise a clear not-found error."""
    profile = PROFILE_STORE.get(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found. Complete onboarding first.",
        )

    return profile


def require_schedule(user_id: str) -> WeeklySchedule:
    """Return saved weekly schedule or raise a clear not-found error."""
    schedule = SCHEDULE_STORE.get(user_id)

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Weekly schedule not found. Save regular timetable first.",
        )

    return schedule
