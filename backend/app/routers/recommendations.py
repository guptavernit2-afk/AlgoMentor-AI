"""
AlgoMentor AI — recommendation endpoint.

POST /api/recommendations
"""

from fastapi import APIRouter

from app.models import (
    ProblemRecommendation,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.recommendation_service import (
    PROBLEM_BANK,
    build_plan_note,
    calculate_match_score,
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
    ranked_problems: list[ProblemRecommendation] = []

    for problem in PROBLEM_BANK:
        score = calculate_match_score(
            problem=problem,
            workload=request.workload,
            situation=request.situation,
            weak_concept=request.weak_concept,
            goal=request.goal,
        )

        ranked_problems.append(
            ProblemRecommendation(
                **problem,
                match_score=score,
            )
        )

    ranked_problems.sort(key=lambda p: p.match_score, reverse=True)

    return RecommendationResponse(
        student_context=request,
        recommendations=ranked_problems,
        plan_note=build_plan_note(request.workload, request.situation),
    )
