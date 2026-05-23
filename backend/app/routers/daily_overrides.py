"""
AlgoMentor AI — daily override / quick check-in endpoints.

PUT    /api/users/{user_id}/daily-overrides/{override_date}
GET    /api/users/{user_id}/daily-overrides/{override_date}
DELETE /api/users/{user_id}/daily-overrides/{override_date}

Storage is delegated to the repository layer (memory or postgres),
selected automatically from STORAGE_BACKEND in the environment.
"""

from datetime import date as Date

from fastapi import APIRouter, HTTPException

from app.models import (
    DailyOverride,
    DailyOverrideDeleteResponse,
    DailyOverrideResponse,
)
from app.repositories.daily_override_repository import get_daily_override_repository
from app.services.daily_override_service import require_daily_override
from app.storage import require_profile, require_schedule


router = APIRouter(prefix="/api/users", tags=["Daily Override"])


@router.put(
    "/{user_id}/daily-overrides/{override_date}",
    response_model=DailyOverrideResponse,
)
def save_daily_override(
    user_id: str,
    override_date: Date,
    override: DailyOverride,
) -> DailyOverrideResponse:
    """
    Save a one-day exception to the student's normal weekly timetable.

    Examples:
    - Internal exam today
    - Assignment workload today
    - Unexpected free day
    - Extra or reduced available study time
    - Low/high energy today

    This does not modify the regular weekly timetable.
    """
    require_profile(user_id)
    require_schedule(user_id)

    try:
        repo = get_daily_override_repository()
        repo.save_override(user_id, override_date, override)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

    return DailyOverrideResponse(
        user_id=user_id,
        date=override_date,
        override=override,
        message="Daily override saved successfully. Regular timetable unchanged.",
    )


@router.get(
    "/{user_id}/daily-overrides/{override_date}",
    response_model=DailyOverrideResponse,
)
def get_daily_override(
    user_id: str,
    override_date: Date,
) -> DailyOverrideResponse:
    """Retrieve a saved one-day schedule/check-in override."""
    override = require_daily_override(user_id, override_date)

    return DailyOverrideResponse(
        user_id=user_id,
        date=override_date,
        override=override,
        message="Daily override retrieved successfully.",
    )


@router.delete(
    "/{user_id}/daily-overrides/{override_date}",
    response_model=DailyOverrideDeleteResponse,
)
def delete_daily_override(
    user_id: str,
    override_date: Date,
) -> DailyOverrideDeleteResponse:
    """
    Remove a one-day override when the student wants
    to return to the normal saved timetable.
    """
    try:
        repo = get_daily_override_repository()
        deleted = repo.delete_override(user_id, override_date)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="No daily override found for this date.",
        )

    return DailyOverrideDeleteResponse(
        user_id=user_id,
        date=override_date,
        message="Daily override removed. Normal weekly timetable will be used.",
    )
