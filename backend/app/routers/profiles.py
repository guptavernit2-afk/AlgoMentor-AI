"""
AlgoMentor AI — student profile endpoints.

PUT /api/users/{user_id}/profile
GET /api/users/{user_id}/profile
"""

from fastapi import APIRouter, HTTPException

from app.models import StudentProfile, StudentProfileResponse
from app.storage import PROFILE_STORE, require_profile


router = APIRouter(prefix="/api/users", tags=["Student Profile"])


@router.put(
    "/{user_id}/profile",
    response_model=StudentProfileResponse,
)
def save_student_profile(
    user_id: str,
    profile: StudentProfile,
) -> StudentProfileResponse:
    """
    Save or update the student's long-term learning profile.

    This data is entered during onboarding and only changed
    later from profile/settings.
    """
    if profile.maximum_daily_minutes < profile.minimum_daily_minutes:
        raise HTTPException(
            status_code=400,
            detail=(
                "Maximum daily minutes must be greater than or equal "
                "to minimum daily minutes."
            ),
        )

    PROFILE_STORE[user_id] = profile

    return StudentProfileResponse(
        user_id=user_id,
        profile=profile,
        message="Student profile saved successfully.",
    )


@router.get(
    "/{user_id}/profile",
    response_model=StudentProfileResponse,
)
def get_student_profile(user_id: str) -> StudentProfileResponse:
    """Retrieve a saved student profile."""
    profile = require_profile(user_id)

    return StudentProfileResponse(
        user_id=user_id,
        profile=profile,
        message="Student profile retrieved successfully.",
    )
