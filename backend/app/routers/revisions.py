"""
AlgoMentor AI — revision history endpoints.

POST /api/users/{user_id}/revision-reviews
GET  /api/users/{user_id}/revision-queue/{as_of_date}
GET  /api/users/{user_id}/revision-history
"""

from datetime import date as Date

from fastapi import APIRouter

from app.models import (
    RevisionQueueResponse,
    TopicReviewRequest,
    TopicReviewResponse,
)
from app.services.sm2_service import (
    get_revision_queue,
    record_topic_review,
)
from app.storage import REVISION_HISTORY_STORE, require_profile


router = APIRouter(prefix="/api/users", tags=["Revision History (SM-2)"])


@router.post(
    "/{user_id}/revision-reviews",
    response_model=TopicReviewResponse,
    status_code=200,
)
def submit_topic_review(
    user_id: str,
    request: TopicReviewRequest,
) -> TopicReviewResponse:
    """
    Record a topic recall quality score and update the SM-2 schedule.

    The topic must match a completed topic or the student's current topic.
    Returns the updated revision state including the next scheduled review date.
    """
    profile = require_profile(user_id)
    new_state = record_topic_review(user_id=user_id, profile=profile, request=request)

    return TopicReviewResponse(
        user_id=user_id,
        state=new_state,
        message="Topic review recorded and next revision scheduled using SM-2.",
    )


@router.get(
    "/{user_id}/revision-queue/{as_of_date}",
    response_model=RevisionQueueResponse,
)
def get_user_revision_queue(
    user_id: str,
    as_of_date: Date,
) -> RevisionQueueResponse:
    """
    Return all SM-2 tracked topics split into due and upcoming lists.

    - due_topics: topics whose next_review_date is on or before as_of_date.
    - upcoming_topics: topics not yet due, sorted by earliest next review.
    - untracked_completed_topics: topics in the profile with no SM-2 state yet.
    """
    profile = require_profile(user_id)
    return get_revision_queue(
        user_id=user_id,
        profile=profile,
        as_of_date=as_of_date,
    )


@router.get(
    "/{user_id}/revision-history",
)
def get_revision_history(user_id: str) -> dict:
    """
    Return the raw review audit trail for debugging and demo purposes.

    Each entry shows what quality was submitted, what interval was assigned,
    and what the next review date became.
    """
    require_profile(user_id)
    history = REVISION_HISTORY_STORE.get(user_id, [])
    return {
        "user_id": user_id,
        "total_records": len(history),
        "history": [r.model_dump() for r in history],
    }
