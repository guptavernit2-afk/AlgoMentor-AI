"""
AlgoMentor AI — weekly schedule endpoints.

PUT /api/users/{user_id}/weekly-schedule
GET /api/users/{user_id}/weekly-schedule
"""

from fastapi import APIRouter, HTTPException

from app.models import WeeklySchedule, WeeklyScheduleResponse
from app.storage import SCHEDULE_STORE, require_schedule


router = APIRouter(prefix="/api/users", tags=["Weekly Schedule"])


@router.put(
    "/{user_id}/weekly-schedule",
    response_model=WeeklyScheduleResponse,
)
def save_weekly_schedule(
    user_id: str,
    schedule: WeeklySchedule,
) -> WeeklyScheduleResponse:
    """
    Save or update the student's regular weekly college timetable.

    The timetable is entered once and reused every day until
    the student updates it.
    """
    submitted_days = [day.day for day in schedule.days]

    if len(set(submitted_days)) != 7:
        raise HTTPException(
            status_code=400,
            detail="Weekly schedule must contain each weekday exactly once.",
        )

    for day_schedule in schedule.days:
        if day_schedule.is_free_day and day_schedule.classes:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"{day_schedule.day} cannot be a free day "
                    "and contain classes."
                ),
            )

    SCHEDULE_STORE[user_id] = schedule

    return WeeklyScheduleResponse(
        user_id=user_id,
        schedule=schedule,
        message="Weekly schedule saved successfully.",
    )


@router.get(
    "/{user_id}/weekly-schedule",
    response_model=WeeklyScheduleResponse,
)
def get_weekly_schedule(user_id: str) -> WeeklyScheduleResponse:
    """Retrieve a saved weekly timetable."""
    schedule = require_schedule(user_id)

    return WeeklyScheduleResponse(
        user_id=user_id,
        schedule=schedule,
        message="Weekly schedule retrieved successfully.",
    )
