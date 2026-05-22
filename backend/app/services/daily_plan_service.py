"""
AlgoMentor AI — daily plan service.

Contains all deterministic study-budget arithmetic, intensity
classification, task generation, and revision-focus derivation.

This module is intentionally free of FastAPI / routing concerns
so the logic can be unit-tested in isolation.
"""

from datetime import date as Date

from app.models import (
    DailyOverride,
    DailyPlanResponse,
    DailyPlanTask,
    DaySchedule,
    PlanIntensity,
    StudentProfile,
    Workload,
    WeakConcept,
)
from app.services.recommendation_service import (
    build_plan_note,
    get_ranked_recommendations,
)


# ============================================================
# Allowed WeakConcept values (mirrors the Literal in models.py)
# ============================================================

_VALID_WEAK_CONCEPTS: frozenset[str] = frozenset(
    [
        "Prefix Sum",
        "Recursion",
        "Binary Search",
        "Sliding Window",
        "Dynamic Programming",
        "Graphs",
    ]
)

_DEFAULT_WEAK_CONCEPT: WeakConcept = "Prefix Sum"

REVISION_NOTE = (
    "Revision focus is currently derived from completed topics. "
    "SM-2 revision history will be integrated in the next phase."
)


# ============================================================
# Time helpers
# ============================================================

def _parse_minutes(time_str: str) -> int:
    """Convert 'HH:MM' to minutes-since-midnight."""
    h, m = time_str.split(":")
    return int(h) * 60 + int(m)


def _class_minutes_for_day(day_schedule: DaySchedule) -> int:
    """Return total class duration in minutes for the given day."""
    total = 0
    for slot in day_schedule.classes:
        start = _parse_minutes(slot.start_time)
        end = _parse_minutes(slot.end_time)
        total += max(0, end - start)
    return total


# ============================================================
# Study-budget calculation
# ============================================================

def compute_available_minutes(
    profile: StudentProfile,
    day_schedule: DaySchedule,
    override: DailyOverride | None,
) -> int:
    """
    Deterministic algorithm to find how many DSA minutes the student
    realistically has on a given day, respecting both the regular
    timetable and any daily override.

    Steps:
      A. Measure class load.
      B. Set base budget from timetable rules.
      C. Apply override adjustments (situation → energy → extra).
      D. Clamp to [0, profile.maximum_daily_minutes].
    """
    min_mins = profile.minimum_daily_minutes
    max_mins = profile.maximum_daily_minutes

    # --- A. Class load ---
    class_mins = _class_minutes_for_day(day_schedule)

    # --- B. Base budget ---
    if day_schedule.is_free_day or class_mins == 0:
        budget = max_mins
    elif class_mins >= 360:
        budget = max(min_mins, round(max_mins * 0.35))
    elif class_mins >= 240:
        budget = max(min_mins, round(max_mins * 0.50))
    else:  # 0 < class_mins < 240
        budget = max(min_mins, round(max_mins * 0.75))

    # --- C. Override adjustments ---
    if override is not None:
        situation = override.situation

        if situation == "Free day":
            budget = max_mins

        elif situation == "Internal exam / Test":
            budget = min_mins

        elif situation in {"Assignment", "Project work", "Event / Hackathon"}:
            budget = max(min_mins, budget - 20)

        # Energy level
        if override.energy_level == "Low":
            budget = max(min_mins, budget - 15)
        elif override.energy_level == "High":
            budget = min(max_mins, budget + 15)

        # Extra minutes from override (can push below min_mins intentionally)
        budget += override.extra_available_minutes

    # --- D. Clamp ---
    budget = max(0, min(budget, max_mins))

    return budget


# ============================================================
# Workload derivation
# ============================================================

def derive_workload(
    profile: StudentProfile,
    available_minutes: int,
    override: DailyOverride | None,
) -> Workload:
    """
    Classify today's workload for recommendation scoring.

    High  → exam day or barely any time left.
    Low   → free day or plenty of study time.
    Medium → everything else.
    """
    situation = override.situation if override is not None else "Normal day"
    max_mins = profile.maximum_daily_minutes
    min_mins = profile.minimum_daily_minutes

    if situation == "Internal exam / Test" or available_minutes <= min_mins:
        return "High"

    if situation == "Free day" or available_minutes >= round(max_mins * 0.75):
        return "Low"

    return "Medium"


# ============================================================
# Plan intensity
# ============================================================

def determine_intensity(
    profile: StudentProfile,
    available_minutes: int,
    override: DailyOverride | None,
) -> PlanIntensity:
    """Classify the overall study-session intensity for the day."""
    situation = override.situation if override is not None else "Normal day"
    max_mins = profile.maximum_daily_minutes
    min_mins = profile.minimum_daily_minutes

    if available_minutes == 0:
        return "Rest"

    if available_minutes <= min_mins + 10 or situation == "Internal exam / Test":
        return "Light"

    if available_minutes >= round(max_mins * 0.75) or situation == "Free day":
        return "Deep"

    return "Balanced"


# ============================================================
# Task generation
# ============================================================

def generate_tasks(
    intensity: PlanIntensity,
    available_minutes: int,
    revision_focus: str | None,
    current_topic: str,
) -> list[DailyPlanTask]:
    """
    Build a practical task list whose total duration never exceeds
    available_minutes.

    Each intensity tier has a fixed pattern; durations are derived
    proportionally from the budget and rounded to whole minutes.
    """
    tasks: list[DailyPlanTask] = []
    rev = revision_focus or current_topic

    if intensity == "Rest":
        tasks.append(
            DailyPlanTask(
                task_id=1,
                title="Rest day — no DSA load",
                topic=current_topic,
                duration_minutes=0,
                task_type="Recovery",
                reason=(
                    "No DSA load scheduled today. "
                    "Rest is an important part of retention."
                ),
            )
        )
        return tasks

    if intensity == "Light":
        # Up to 2 tasks; split budget roughly 50/50
        half = available_minutes // 2
        rest = available_minutes - half

        if revision_focus:
            tasks.append(
                DailyPlanTask(
                    task_id=1,
                    title=f"Quick {rev} recall",
                    topic=rev,
                    duration_minutes=half,
                    task_type="Revision",
                    reason=(
                        f"Short revision of {rev} to keep recently studied "
                        "patterns fresh without heavy cognitive load."
                    ),
                )
            )
            tasks.append(
                DailyPlanTask(
                    task_id=2,
                    title=f"Review {current_topic} pattern notes",
                    topic=current_topic,
                    duration_minutes=rest,
                    task_type="Current Topic",
                    reason=(
                        f"Light read-through of {current_topic} notes "
                        "to maintain familiarity on a busy day."
                    ),
                )
            )
        else:
            tasks.append(
                DailyPlanTask(
                    task_id=1,
                    title=f"Review {current_topic} pattern notes",
                    topic=current_topic,
                    duration_minutes=available_minutes,
                    task_type="Current Topic",
                    reason=(
                        f"Focused read-through of {current_topic} "
                        "keeping the session light."
                    ),
                )
            )
        return tasks

    if intensity == "Balanced":
        # 3 tasks: ~40% revision / ~40% current-topic / ~20% review
        rev_mins = round(available_minutes * 0.40)
        topic_mins = round(available_minutes * 0.40)
        review_mins = available_minutes - rev_mins - topic_mins

        if revision_focus:
            tasks.append(
                DailyPlanTask(
                    task_id=1,
                    title=f"Solve one {rev} recall problem",
                    topic=rev,
                    duration_minutes=rev_mins,
                    task_type="Revision",
                    reason=(
                        f"Revisiting {rev} reinforces retention of a "
                        "previously completed topic."
                    ),
                )
            )
        else:
            topic_mins += rev_mins  # absorb into current-topic slot
            rev_mins = 0

        tasks.append(
            DailyPlanTask(
                task_id=2 if revision_focus else 1,
                title=f"Practice {current_topic} problem",
                topic=current_topic,
                duration_minutes=topic_mins,
                task_type="Current Topic",
                reason=(
                    f"Active problem-solving on {current_topic} builds "
                    "fluency with the current learning objective."
                ),
            )
        )
        tasks.append(
            DailyPlanTask(
                task_id=3 if revision_focus else 2,
                title="Review session — reflect on today's problems",
                topic=current_topic,
                duration_minutes=review_mins,
                task_type="Review",
                reason=(
                    "A short review pass cements patterns and surfaces "
                    "any gaps before the next session."
                ),
            )
        )
        return tasks

    # intensity == "Deep"
    # 4 tasks: ~25% revision / ~35% current-topic / ~25% mixed / ~15% review
    rev_mins   = round(available_minutes * 0.25)
    topic_mins = round(available_minutes * 0.35)
    mixed_mins = round(available_minutes * 0.25)
    review_mins = available_minutes - rev_mins - topic_mins - mixed_mins

    if revision_focus:
        tasks.append(
            DailyPlanTask(
                task_id=1,
                title=f"Deep {rev} revision problem",
                topic=rev,
                duration_minutes=rev_mins,
                task_type="Revision",
                reason=(
                    f"Deep revision of {rev} on a free/high-time day "
                    "for stronger long-term retention."
                ),
            )
        )
    else:
        topic_mins += rev_mins
        rev_mins = 0

    tasks.append(
        DailyPlanTask(
            task_id=2 if revision_focus else 1,
            title=f"Solve {current_topic} challenge problem",
            topic=current_topic,
            duration_minutes=topic_mins,
            task_type="Current Topic",
            reason=(
                f"Extended {current_topic} practice takes advantage of "
                "the larger time budget available today."
            ),
        )
    )
    tasks.append(
        DailyPlanTask(
            task_id=3 if revision_focus else 2,
            title="Mixed practice — recommended problem set",
            topic="Mixed",
            duration_minutes=mixed_mins,
            task_type="Mixed Practice",
            reason=(
                "Mixed problems from today's recommended set reinforce "
                "pattern recognition across topics."
            ),
        )
    )
    tasks.append(
        DailyPlanTask(
            task_id=4 if revision_focus else 3,
            title="Reflection and review session",
            topic=current_topic,
            duration_minutes=review_mins,
            task_type="Review",
            reason=(
                "End-of-session review solidifies what was practised "
                "and highlights areas for the next session."
            ),
        )
    )
    return tasks


# ============================================================
# Revision focus + weak concept resolution
# ============================================================

def resolve_revision_focus(profile: StudentProfile) -> str | None:
    """
    Return the first completed topic as the revision focus, or None
    if the student has not yet completed any topics.
    """
    if profile.completed_topics:
        return profile.completed_topics[0]
    return None


def resolve_weak_concept(profile: StudentProfile) -> str:
    """
    Return the first weak concept from the profile if it matches one
    of the allowed WeakConcept Literal values; otherwise fall back to
    the default so recommendation scoring is always valid.
    """
    for concept in profile.weak_concepts:
        if concept in _VALID_WEAK_CONCEPTS:
            return concept
    return _DEFAULT_WEAK_CONCEPT


# ============================================================
# Plan reason builder
# ============================================================

def build_daily_plan_reason(
    intensity: PlanIntensity,
    available_minutes: int,
    day_schedule: DaySchedule,
    override: DailyOverride | None,
) -> str:
    """Human-readable explanation for why this plan was produced."""
    situation = override.situation if override is not None else "Normal day"

    parts: list[str] = []

    if override is not None:
        parts.append(f"A daily override is active (situation: {situation}).")

    if day_schedule.is_free_day:
        parts.append("Today is a scheduled free day in the regular timetable.")
    else:
        class_mins = _class_minutes_for_day(day_schedule)
        if class_mins > 0:
            parts.append(
                f"{day_schedule.day} has {class_mins} minutes of college classes "
                "in the regular timetable."
            )

    parts.append(
        f"Available study time was calculated as {available_minutes} minutes, "
        f"resulting in a {intensity} intensity plan."
    )

    return " ".join(parts)


# ============================================================
# Main daily plan builder
# ============================================================

def build_daily_plan(
    user_id: str,
    plan_date: Date,
    profile: StudentProfile,
    day_schedule: DaySchedule,
    override: DailyOverride | None,
) -> DailyPlanResponse:
    """
    Orchestrate all sub-calculations and return a fully populated
    DailyPlanResponse.  No I/O or HTTP concerns here.
    """
    # Study budget
    available_minutes = compute_available_minutes(profile, day_schedule, override)

    # Derived attributes
    workload   = derive_workload(profile, available_minutes, override)
    intensity  = determine_intensity(profile, available_minutes, override)

    revision_focus = resolve_revision_focus(profile)
    weak_concept   = resolve_weak_concept(profile)

    # Recommendations (shared scoring)
    situation = override.situation if override is not None else "Normal day"
    recommended_problems = get_ranked_recommendations(
        workload=workload,
        situation=situation,
        weak_concept=weak_concept,
        goal=profile.goal,
    )

    # Tasks
    tasks = generate_tasks(
        intensity=intensity,
        available_minutes=available_minutes,
        revision_focus=revision_focus,
        current_topic=profile.current_topic,
    )

    # Human-readable reasoning
    plan_reason = build_daily_plan_reason(
        intensity=intensity,
        available_minutes=available_minutes,
        day_schedule=day_schedule,
        override=override,
    )

    return DailyPlanResponse(
        user_id=user_id,
        date=plan_date,
        day_name=day_schedule.day,
        schedule_for_today=day_schedule,
        override_applied=override is not None,
        daily_override=override,
        derived_workload=workload,
        plan_intensity=intensity,
        available_minutes=available_minutes,
        revision_focus=revision_focus,
        current_topic=profile.current_topic,
        tasks=tasks,
        recommended_problems=recommended_problems,
        plan_reason=plan_reason,
        revision_note=REVISION_NOTE,
    )
