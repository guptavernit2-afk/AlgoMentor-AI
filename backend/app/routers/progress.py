"""
Router for student progress and activity endpoints.
"""

from fastapi import APIRouter

from app.models import ProgressResponse
from app.services.progress_service import get_user_progress

router = APIRouter(prefix="/api/users", tags=["Progress"])


@router.get("/{user_id}/progress", response_model=ProgressResponse)
def get_progress_endpoint(user_id: str) -> ProgressResponse:
    """
    Returns the user's progress stats and 365-day activity graph data.
    """
    return get_user_progress(user_id)
