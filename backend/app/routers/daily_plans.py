"""
AlgoMentor AI — Smart Daily Plan endpoint.

GET /api/users/{user_id}/daily-plan/{plan_date}

Reads the saved student profile and weekly timetable, applies any
optional daily override for the requested date, and returns a fully
computed study plan without asking the student to re-enter data.
"""

from datetime import date as Date

from fastapi import APIRouter, HTTPException

from app.models import DailyPlanResponse
from app.services.daily_plan_service import build_daily_plan
from app.storage import (
    DAILY_OVERRIDE_STORE,
    require_profile,
    require_schedule,
)


router = APIRouter(prefix="/api/users", tags=["Smart Daily Plan"])


# Weekday number (0=Monday … 6=Sunday) → DayName
_WEEKDAY_TO_NAME = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


@router.get(
    "/{user_id}/daily-plan/{plan_date}",
    response_model=DailyPlanResponse,
)
def get_daily_plan(
    user_id: str,
    plan_date: Date,
) -> DailyPlanResponse:
    """
    Generate a personalised Smart Daily Plan for a specific date.

    The plan is built automatically from:
    - The student's saved profile (goal, topics, study limits).
    - The regular weekly timetable for that weekday.
    - An optional daily override for that exact date.

    The weekly timetable is NEVER modified by this endpoint.
    """
    profile  = require_profile(user_id)
    schedule = require_schedule(user_id)

    # Determine which weekday the plan_date falls on
    day_name = _WEEKDAY_TO_NAME[plan_date.weekday()]

    # Find the matching DaySchedule in the saved weekly timetable
    day_schedule = next(
        (d for d in schedule.days if d.day == day_name),
        None,
    )

    if day_schedule is None:
        # This should never happen if the timetable was saved correctly,
        # but guard defensively.
        raise HTTPException(
            status_code=422,
            detail=(
                f"No schedule entry found for {day_name}. "
                "Please re-save your weekly timetable."
            ),
        )

    # Look up any daily override for this exact date
    override = DAILY_OVERRIDE_STORE.get((user_id, plan_date))

    # Delegate all computation to the service layer
    return build_daily_plan(
        user_id=user_id,
        plan_date=plan_date,
        profile=profile,
        day_schedule=day_schedule,
        override=override,
    )
