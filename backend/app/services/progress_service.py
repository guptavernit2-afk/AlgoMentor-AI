"""
AlgoMentor AI — progress service.

Provides deterministic mock progress data (activity graph and KPIs)
for the dashboard, mimicking a 365-day contribution history.
"""

import random
from datetime import date as Date
from datetime import timedelta

from app.models import DifficultyCounts, ProgressResponse, ProgressStats


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
        memory_retention_percent=92  # Mock solid retention
    )

    return ProgressResponse(
        user_id=user_id,
        stats=stats,
        activity_graph=activity_graph
    )
