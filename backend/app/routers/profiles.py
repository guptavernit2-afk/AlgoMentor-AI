"""
AlgoMentor AI — student profile endpoints.

PUT /api/users/{user_id}/profile
GET /api/users/{user_id}/profile

Storage is delegated to the repository layer (memory or postgres),
selected automatically from STORAGE_BACKEND in the environment.
"""

from fastapi import APIRouter, HTTPException

from app.models import StudentProfile, StudentProfileResponse
from app.repositories.profile_repository import get_profile_repository
from app.services.profile_service import require_profile


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

    try:
        repo = get_profile_repository()
        repo.save_profile(user_id, profile)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None

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
