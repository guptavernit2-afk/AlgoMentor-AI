"""
AlgoMentor AI — Pydantic models and shared Literal types.

All request bodies, response schemas, and named Literal aliases live here
so that routers, services, and tests can import from a single location.
"""

from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# Shared Literal Types
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

EnergyLevel = Literal["Low", "Normal", "High"]

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
# Daily Override / Quick Check-in Models
# ============================================================

class DailyOverride(BaseModel):
    situation: Situation = "Normal day"
    extra_available_minutes: int = Field(
        default=0,
        ge=-240,
        le=480,
        description=(
            "Temporary change in available DSA time for this date. "
            "Positive adds time; negative reduces time."
        ),
    )
    energy_level: EnergyLevel = "Normal"
    note: str | None = Field(default=None, max_length=200)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "situation": "Internal exam / Test",
                    "extra_available_minutes": 0,
                    "energy_level": "Low",
                    "note": "Physics internal exam today",
                }
            ]
        }
    }


class DailyOverrideResponse(BaseModel):
    user_id: str
    date: Date
    override: DailyOverride
    message: str


class DailyOverrideDeleteResponse(BaseModel):
    user_id: str
    date: Date
    message: str


# ============================================================
# Daily Plan Models
# ============================================================

PlanIntensity = Literal["Rest", "Light", "Balanced", "Deep"]

TaskType = Literal["Revision", "Current Topic", "Mixed Practice", "Review", "Recovery"]


class DailyPlanTask(BaseModel):
    task_id: int
    title: str
    topic: str
    duration_minutes: int
    task_type: TaskType
    reason: str


class DailyPlanResponse(BaseModel):
    user_id: str
    date: Date
    day_name: str
    schedule_for_today: "DaySchedule"
    override_applied: bool
    daily_override: "DailyOverride | None"
    derived_workload: Workload
    plan_intensity: PlanIntensity
    available_minutes: int
    revision_focus: str | None
    current_topic: str
    tasks: list[DailyPlanTask]
    recommended_problems: list["ProblemRecommendation"]
    plan_reason: str
    revision_note: str


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
