"""
AlgoMentor AI — Daily Override service helpers.

Provides two gateway functions used by routers and the daily plan service:

    require_daily_override(user_id, override_date)
        → Returns override or raises HTTP 404 (for GET/DELETE endpoints).

    get_optional_daily_override(user_id, override_date)
        → Returns override or None (for Smart Daily Plan — no error if absent).

Both delegate to whichever repository implementation is active (memory or
postgres), determined once at startup by `get_daily_override_repository()`.

Import from this module or from `app.storage` (which re-exports both) so no
existing call-site changes are required.
"""

from datetime import date as Date

from fastapi import HTTPException

from app.models import DailyOverride
from app.repositories.daily_override_repository import get_daily_override_repository


def require_daily_override(user_id: str, override_date: Date) -> DailyOverride:
    """
    Return the saved daily override for (user_id, override_date), or raise HTTP 404.

    Used by the GET and DELETE endpoints where a missing override is an error.
    Converts RuntimeError (DB failure) to HTTP 503.
    """
    repo = get_daily_override_repository()

    try:
        override = repo.get_override(user_id, override_date)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

    if override is None:
        raise HTTPException(
            status_code=404,
            detail="No daily override found for this date.",
        )

    return override


def get_optional_daily_override(
    user_id: str, override_date: Date
) -> DailyOverride | None:
    """
    Return the saved daily override for (user_id, override_date), or None.

    Used by the Smart Daily Plan where a missing override is normal — the
    plan proceeds using the regular weekly timetable.
    Converts RuntimeError (DB failure) to HTTP 503.
    """
    repo = get_daily_override_repository()

    try:
        return repo.get_override(user_id, override_date)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None
