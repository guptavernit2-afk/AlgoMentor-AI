"""
AlgoMentor AI — Weekly Schedule service helpers.

Provides `require_schedule(user_id)` as a single importable function that
works correctly in both storage modes:

  - memory   → reads from in-memory SCHEDULE_STORE via MemoryScheduleRepository
  - postgres → reads from Supabase via PostgresScheduleRepository

All routers and services that currently call `require_schedule` continue to
import it from `app.storage` (which re-exports it from here) so no call site
changes are needed across the codebase.
"""

from fastapi import HTTPException

from app.models import WeeklySchedule
from app.repositories.schedule_repository import get_schedule_repository


def require_schedule(user_id: str) -> WeeklySchedule:
    """
    Return the saved weekly schedule for `user_id`, or raise HTTP 404.

    Delegates to whichever repository implementation is active
    (memory or postgres), determined once at startup by `get_schedule_repository()`.

    This is the single authoritative guard used by:
      - GET  /api/users/{user_id}/weekly-schedule
      - daily override endpoints
      - daily plan endpoints
    """
    repo = get_schedule_repository()

    try:
        schedule = repo.get_schedule(user_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Weekly schedule not found. Save regular timetable first.",
        )

    return schedule
