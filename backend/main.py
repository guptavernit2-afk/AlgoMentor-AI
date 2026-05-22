from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="AlgoMentor AI API",
    description="Backend API for the AlgoMentor AI DSA revision coach.",
    version="0.3.0",
)


# ============================================================
# Shared types
# ============================================================

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

StudyTime = Literal["Morning", "Afternoon", "Evening", "Night"]

DayName = Literal[
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


# ============================================================
# Student Profile Models
# ============================================================

class StudentProfile(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    goal: Goal = "Placement Prep"
    current_topic: str = Field(default="Hashing", min_length=2, max_length=50)
    completed_topics: list[str] = Field(default_factory=lambda: ["Arrays"])
    weak_concepts: list[str] = Field(default_factory=lambda: ["Prefix Sum"])
    preferred_study_time: StudyTime = "Evening"
    minimum_daily_minutes: int = Field(default=20, ge=10, le=240)
    maximum_daily_minutes: int = Field(default=120, ge=20, le=480)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Vernit",
                    "goal": "Placement Prep",
                    "current_topic": "Hashing",
                    "completed_topics": ["Arrays"],
                    "weak_concepts": ["Prefix Sum"],
                    "preferred_study_time": "Evening",
                    "minimum_daily_minutes": 20,
                    "maximum_daily_minutes": 120,
                }
            ]
        }
    }


class StudentProfileResponse(BaseModel):
    user_id: str
    profile: StudentProfile
    message: str


# ============================================================
# Weekly Schedule Models
# ============================================================

class ClassSlot(BaseModel):
    title: str = Field(default="College Classes", min_length=2, max_length=80)
    start_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


class DaySchedule(BaseModel):
    day: DayName
    is_free_day: bool = False
    classes: list[ClassSlot] = Field(default_factory=list)


class WeeklySchedule(BaseModel):
    days: list[DaySchedule] = Field(min_length=7, max_length=7)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "days": [
                        {
                            "day": "Monday",
                            "is_free_day": False,
                            "classes": [
                                {
                                    "title": "College Classes",
                                    "start_time": "09:00",
                                    "end_time": "16:00",
                                }
                            ],
                        },
                        {
                            "day": "Tuesday",
                            "is_free_day": False,
                            "classes": [
                                {
                                    "title": "College Classes",
                                    "start_time": "09:00",
                                    "end_time": "13:00",
                                }
                            ],
                        },
                        {
                            "day": "Wednesday",
                            "is_free_day": False,
                            "classes": [
                                {
                                    "title": "College Classes",
                                    "start_time": "09:00",
                                    "end_time": "16:00",
                                }
                            ],
                        },
                        {
                            "day": "Thursday",
                            "is_free_day": False,
                            "classes": [
                                {
                                    "title": "College Classes",
                                    "start_time": "10:00",
                                    "end_time": "15:00",
                                }
                            ],
                        },
                        {
                            "day": "Friday",
                            "is_free_day": False,
                            "classes": [
                                {
                                    "title": "College Classes",
                                    "start_time": "09:00",
                                    "end_time": "14:00",
                                }
                            ],
                        },
                        {
                            "day": "Saturday",
                            "is_free_day": True,
                            "classes": [],
                        },
                        {
                            "day": "Sunday",
                            "is_free_day": True,
                            "classes": [],
                        },
                    ]
                }
            ]
        }
    }


class WeeklyScheduleResponse(BaseModel):
    user_id: str
    schedule: WeeklySchedule
    message: str


# ============================================================
# Recommendation Models
# ============================================================

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


# ============================================================
# Temporary In-Memory Storage
# Later this will be replaced by Supabase
# ============================================================

PROFILE_STORE: dict[str, StudentProfile] = {}
SCHEDULE_STORE: dict[str, WeeklySchedule] = {}


# ============================================================
# Temporary Problem Bank
# Later this will come from Supabase
# ============================================================

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


# ============================================================
# Recommendation Logic
# ============================================================

def calculate_match_score(
    problem: dict,
    workload: Workload,
    situation: Situation,
    weak_concept: WeakConcept,
    goal: Goal,
) -> int:
    """
    Calculate an explainable problem recommendation score.

    Later, actual revision history and SM-2 priority will also
    be included in this score.
    """
    score = 62
    tags = problem["tags"]
    difficulty = problem["difficulty"]

    if "Hashing" in tags:
        score += 12

    if "Array" in tags:
        score += 10

    if weak_concept in tags:
        score += 16

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


# ============================================================
# General API Endpoints
# ============================================================

@app.get("/")
def read_root() -> dict[str, str]:
    """Confirm that the backend server is running."""
    return {"message": "AlgoMentor AI backend is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health endpoint used to verify API availability."""
    return {"status": "healthy"}


# ============================================================
# Student Profile Endpoints
# ============================================================

@app.put(
    "/api/users/{user_id}/profile",
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
            detail="Maximum daily minutes must be greater than or equal to minimum daily minutes.",
        )

    PROFILE_STORE[user_id] = profile

    return StudentProfileResponse(
        user_id=user_id,
        profile=profile,
        message="Student profile saved successfully.",
    )


@app.get(
    "/api/users/{user_id}/profile",
    response_model=StudentProfileResponse,
)
def get_student_profile(user_id: str) -> StudentProfileResponse:
    """Retrieve a saved student profile."""
    profile = PROFILE_STORE.get(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found.",
        )

    return StudentProfileResponse(
        user_id=user_id,
        profile=profile,
        message="Student profile retrieved successfully.",
    )


# ============================================================
# Weekly Schedule Endpoints
# ============================================================

@app.put(
    "/api/users/{user_id}/weekly-schedule",
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
                detail=f"{day_schedule.day} cannot be a free day and contain classes.",
            )

    SCHEDULE_STORE[user_id] = schedule

    return WeeklyScheduleResponse(
        user_id=user_id,
        schedule=schedule,
        message="Weekly schedule saved successfully.",
    )


@app.get(
    "/api/users/{user_id}/weekly-schedule",
    response_model=WeeklyScheduleResponse,
)
def get_weekly_schedule(user_id: str) -> WeeklyScheduleResponse:
    """Retrieve a saved weekly timetable."""
    schedule = SCHEDULE_STORE.get(user_id)

    if schedule is None:
        raise HTTPException(
            status_code=404,
            detail="Weekly schedule not found.",
        )

    return WeeklyScheduleResponse(
        user_id=user_id,
        schedule=schedule,
        message="Weekly schedule retrieved successfully.",
    )


# ============================================================
# Recommendation Endpoint
# ============================================================

@app.post(
    "/api/recommendations",
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