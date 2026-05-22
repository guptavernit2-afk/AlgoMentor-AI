"""
AlgoMentor AI — weekly schedule endpoints.

PUT /api/users/{user_id}/weekly-schedule
GET /api/users/{user_id}/weekly-schedule
"""

from fastapi import APIRouter, HTTPException

from app.models import WeeklySchedule, WeeklyScheduleResponse
from app.storage import SCHEDULE_STORE, require_schedule


router = APIRouter(prefix="/api/users", tags=["Weekly Schedule"])


# ============================================================
# Internal validation helpers
# ============================================================

def _parse_minutes(time_str: str) -> int:
    """Convert 'HH:MM' string to minutes-since-midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _validate_class_slots(schedule: WeeklySchedule) -> None:
    """
    Raise 400 if any day contains:
    - A class slot where end_time <= start_time.
    - Two class slots on the same day that overlap.
    """
    for day_schedule in schedule.days:
        slots = day_schedule.classes
        if not slots:
            continue

        intervals: list[tuple[int, int]] = []
        for slot in slots:
            start = _parse_minutes(slot.start_time)
            end = _parse_minutes(slot.end_time)

            if end <= start:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{day_schedule.day}: class '{slot.title}' has "
                        f"end_time ({slot.end_time}) not later than "
                        f"start_time ({slot.start_time})."
                    ),
                )

            intervals.append((start, end))

        # Overlap check: sort by start, then see if consecutive intervals cross
        intervals.sort()
        for i in range(len(intervals) - 1):
            if intervals[i][1] > intervals[i + 1][0]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{day_schedule.day}: two class slots overlap — "
                        f"one ends at minute {intervals[i][1]} while the "
                        f"next starts at minute {intervals[i + 1][0]}."
                    ),
                )


# ============================================================
# Endpoints
# ============================================================

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

    # New: time-range and overlap validation
    _validate_class_slots(schedule)

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
