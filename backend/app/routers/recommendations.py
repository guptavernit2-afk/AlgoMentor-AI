"""
AlgoMentor AI — recommendation endpoint.

POST /api/recommendations
"""

from fastapi import APIRouter

from app.models import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import (
    build_plan_note,
    get_ranked_recommendations,
)


router = APIRouter(prefix="/api", tags=["Recommendations"])


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
)
def get_recommendations(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Rank practice problems according to the student's daily context.

    Later, this endpoint will use saved profile, timetable,
    daily overrides, and revision history automatically.
    """
    ranked_problems = get_ranked_recommendations(
        workload=request.workload,
        situation=request.situation,
        weak_concept=request.weak_concept,
        goal=request.goal,
    )

    return RecommendationResponse(
        student_context=request,
        recommendations=ranked_problems,
        plan_note=build_plan_note(request.workload, request.situation),
    )
