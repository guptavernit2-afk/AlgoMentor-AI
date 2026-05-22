from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title="AlgoMentor AI API",
    description="Backend API for the AlgoMentor AI DSA revision coach.",
    version="0.2.0",
)


# -----------------------------
# Request and response models
# -----------------------------

Workload = Literal["Low", "Medium", "High"]

Situation = Literal[
    "Normal day",
    "Assignment",
    "Internal exam / Test",
    "Project work",
    "Event / Hackathon",
    "Free day",
]

WeakConcept = Literal[
    "Prefix Sum",
    "Recursion",
    "Binary Search",
    "Sliding Window",
    "Dynamic Programming",
    "Graphs",
]

Goal = Literal[
    "Beginner DSA",
    "College Practice",
    "Internship Prep",
    "Placement Prep",
    "Competitive Programming",
]


class RecommendationRequest(BaseModel):
    workload: Workload = "Medium"
    situation: Situation = "Normal day"
    weak_concept: WeakConcept = "Prefix Sum"
    goal: Goal = "Placement Prep"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "workload": "High",
                    "situation": "Internal exam / Test",
                    "weak_concept": "Prefix Sum",
                    "goal": "Placement Prep",
                }
            ]
        }
    }


class ProblemRecommendation(BaseModel):
    id: int
    title: str
    difficulty: str
    tags: list[str]
    reason: str
    leetcode_link: str
    match_score: int


class RecommendationResponse(BaseModel):
    student_context: RecommendationRequest
    recommendations: list[ProblemRecommendation]
    plan_note: str


# -----------------------------
# Temporary problem bank
# Later this will come from DB
# -----------------------------

PROBLEM_BANK = [
    {
        "id": 1,
        "title": "Two Sum",
        "difficulty": "Easy",
        "tags": ["Array", "Hashing"],
        "reason": (
            "Refreshes array traversal while strengthening "
            "hash map lookup."
        ),
        "leetcode_link": "https://leetcode.com/problems/two-sum/",
    },
    {
        "id": 2,
        "title": "Contains Duplicate",
        "difficulty": "Easy",
        "tags": ["Array", "Set"],
        "reason": (
            "A quick recall problem for arrays and "
            "set-based duplicate detection."
        ),
        "leetcode_link": "https://leetcode.com/problems/contains-duplicate/",
    },
    {
        "id": 3,
        "title": "Subarray Sum Equals K",
        "difficulty": "Medium",
        "tags": ["Prefix Sum", "Hashing"],
        "reason": (
            "Connects Prefix Sum with Hashing for "
            "stronger pattern understanding."
        ),
        "leetcode_link": "https://leetcode.com/problems/subarray-sum-equals-k/",
    },
]


# -----------------------------
# Recommendation logic
# -----------------------------

def calculate_match_score(
    problem: dict,
    workload: Workload,
    situation: Situation,
    weak_concept: WeakConcept,
    goal: Goal,
) -> int:
    """
    Calculate an explainable problem recommendation score.

    This follows the same prototype scoring idea currently shown
    in the React dashboard. Later, database history and SM-2
    revision priority will be added here.
    """
    score = 62
    tags = problem["tags"]
    difficulty = problem["difficulty"]

    # Current learning journey:
    # Arrays revision is due while the student is learning Hashing.
    if "Hashing" in tags:
        score += 12

    if "Array" in tags:
        score += 10

    # Reinforce the learner's selected weak concept.
    if weak_concept in tags:
        score += 16

    # Goal-based adjustment.
    if goal == "Placement Prep":
        if "Hashing" in tags:
            score += 6
        if difficulty == "Medium":
            score += 4

    elif goal == "Beginner DSA":
        if difficulty == "Easy":
            score += 12
        if difficulty == "Medium":
            score -= 10

    elif goal == "Competitive Programming":
        if difficulty == "Medium":
            score += 12
        if "Prefix Sum" in tags:
            score += 8

    elif goal == "Internship Prep":
        if difficulty in {"Easy", "Medium"}:
            score += 5

    # Workload and daily-life adjustment.
    if workload == "High" or situation == "Internal exam / Test":
        if difficulty == "Easy":
            score += 8
        if difficulty == "Medium":
            score -= 18

    if workload == "Low" or situation == "Free day":
        if difficulty == "Medium":
            score += 10

    if situation in {"Assignment", "Project work"}:
        if difficulty == "Easy":
            score += 6
        if difficulty == "Medium":
            score -= 8

    return max(45, min(score, 98))


def build_plan_note(workload: Workload, situation: Situation) -> str:
    """Return a short explanation of today's recommendation strategy."""
    if situation == "Internal exam / Test":
        return "Exam day detected: prioritising quick recall and light practice."

    if workload == "High" or situation in {"Assignment", "Project work"}:
        return "Busy day detected: prioritising easy revision problems."

    if workload == "Low" or situation == "Free day":
        return "More time available: medium reinforcement problems are boosted."

    return "Balanced day: combining revision with current-topic practice."


# -----------------------------
# API endpoints
# -----------------------------

@app.get("/")
def read_root() -> dict[str, str]:
    """Confirm that the backend server is running."""
    return {"message": "AlgoMentor AI backend is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health endpoint used to verify API availability."""
    return {"status": "healthy"}


@app.post("/api/recommendations", response_model=RecommendationResponse)
def get_recommendations(
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Rank practice problems according to the student's daily context.

    The React frontend can later send its dropdown selections here
    instead of calculating recommendation scores locally.
    """
    ranked_problems = []

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

    ranked_problems.sort(key=lambda problem: problem.match_score, reverse=True)

    return RecommendationResponse(
        student_context=request,
        recommendations=ranked_problems,
        plan_note=build_plan_note(request.workload, request.situation),
    )