"""
AlgoMentor AI — daily override / quick check-in endpoints.

PUT    /api/users/{user_id}/daily-overrides/{override_date}
GET    /api/users/{user_id}/daily-overrides/{override_date}
DELETE /api/users/{user_id}/daily-overrides/{override_date}
"""

from datetime import date as Date

from fastapi import APIRouter, HTTPException

from app.models import (
    DailyOverride,
    DailyOverrideDeleteResponse,
    DailyOverrideResponse,
)
from app.storage import (
    DAILY_OVERRIDE_STORE,
    require_profile,
    require_schedule,
)


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

    DAILY_OVERRIDE_STORE[(user_id, override_date)] = override

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
    override = DAILY_OVERRIDE_STORE.get((user_id, override_date))

    if override is None:
        raise HTTPException(
            status_code=404,
            detail="No daily override found for this date.",
        )

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
    key = (user_id, override_date)

    if key not in DAILY_OVERRIDE_STORE:
        raise HTTPException(
            status_code=404,
            detail="No daily override found for this date.",
        )

    del DAILY_OVERRIDE_STORE[key]

    return DailyOverrideDeleteResponse(
        user_id=user_id,
        date=override_date,
        message="Daily override removed. Normal weekly timetable will be used.",
    )
