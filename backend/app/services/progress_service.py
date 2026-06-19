"""
AlgoMentor AI — progress service.

Provides deterministic mock progress data (activity graph and KPIs)
for the dashboard, mimicking a 365-day contribution history.
"""

import random
from datetime import date as Date
from datetime import timedelta

from app.models import (
    AccuracyDataPoint,
    DifficultyCounts,
    FocusArea,
    ProgressResponse,
    ProgressStats,
    StudyHoursDataPoint,
    TopicMastery,
)


def _deterministic_seed(user_id: str) -> int:
    """Returns a simple seed based on the user ID."""
    return sum(ord(c) for c in user_id)


def generate_mock_activity_graph(seed: int) -> dict[str, int]:
    """
    Generates a 365-day history ending today.
    Uses a seeded random generator so the graph is stable across refreshes.
    """
    random.seed(seed)
    activity_graph = {}
    today = Date.today()

    for i in range(365):
        d = today - timedelta(days=364 - i)
        date_str = d.isoformat()

        # Decide if this day has activity
        # Weekends might have more activity, or randomly dropped days
        base_prob = 0.6 if d.weekday() < 5 else 0.8
        
        if random.random() < base_prob:
            # 1 to 5 problems solved
            count = random.randint(1, 4)
            # Occasional big days
            if random.random() < 0.1:
                count += random.randint(2, 4)
            activity_graph[date_str] = count
        else:
            activity_graph[date_str] = 0

    # Ensure today has some activity for the demo effect
    activity_graph[today.isoformat()] = random.randint(1, 3)
    return activity_graph


def get_user_progress(user_id: str) -> ProgressResponse:
    """
    Returns the ProgressResponse for the given user.
    """
    seed = _deterministic_seed(user_id)
    activity_graph = generate_mock_activity_graph(seed)

    # Calculate total solved from graph
    total_solved = sum(activity_graph.values())
    
    # Deterministic split based on total
    easy_count = int(total_solved * 0.5)
    medium_count = int(total_solved * 0.4)
    hard_count = total_solved - easy_count - medium_count

    # Calculate current streak
    streak = 0
    today = Date.today()
    for i in range(365):
        d = today - timedelta(days=i)
        if activity_graph.get(d.isoformat(), 0) > 0:
            streak += 1
        else:
            break

    stats = ProgressStats(
        total_solved=total_solved,
        difficulty_counts=DifficultyCounts(
            Easy=easy_count,
            Medium=medium_count,
            Hard=hard_count
        ),
        current_streak=streak,
        memory_retention_percent=89,
        study_time_hours=142,
        rank="Top 5% - Master Rank"
    )

    # 1. Generate Accuracy Trend (30 days)
    accuracy_trend = []
    base_accuracy = 75
    for i in range(29, -1, -1):
        d = today - timedelta(days=i)
        # Random walk up to 90s
        base_accuracy += random.randint(-2, 3)
        base_accuracy = max(50, min(100, base_accuracy))
        accuracy_trend.append(AccuracyDataPoint(
            date=d.strftime("%b %d"),
            accuracy=base_accuracy
        ))
    
    # Force the latest to match the KPI stat (89%)
    accuracy_trend[-1].accuracy = 89

    # 2. Generate Weekly Study Hours
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # Reorder so today is at the end, or just map standard Mon-Sun
    study_hours = [
        StudyHoursDataPoint(day="Mon", hours=3.5),
        StudyHoursDataPoint(day="Tue", hours=5.2),
        StudyHoursDataPoint(day="Wed", hours=2.1),
        StudyHoursDataPoint(day="Thu", hours=4.8),
        StudyHoursDataPoint(day="Fri", hours=6.1),
        StudyHoursDataPoint(day="Sat", hours=8.4),
        StudyHoursDataPoint(day="Sun", hours=5.5),
    ]

    # 3. Topic Mastery
    topic_mastery = [
        TopicMastery(topic="Arrays", percentage=95),
        TopicMastery(topic="Two Pointers", percentage=82),
        TopicMastery(topic="Sliding Window", percentage=60),
        TopicMastery(topic="Binary Search", percentage=45),
        TopicMastery(topic="Dynamic Programming", percentage=30),
        TopicMastery(topic="Graphs", percentage=15),
    ]

    # 4. Focus Areas
    focus_areas = [
        FocusArea(topic="Binary Search", reason="Needs more practice"),
        FocusArea(topic="Dynamic Programming", reason="Keep practicing"),
        FocusArea(topic="Graphs", reason="Start your journey"),
    ]

    return ProgressResponse(
        user_id=user_id,
        stats=stats,
        activity_graph=activity_graph,
        accuracy_trend=accuracy_trend,
        study_hours=study_hours,
        topic_mastery=topic_mastery,
        focus_areas=focus_areas
    )
