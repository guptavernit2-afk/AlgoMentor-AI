"""
AlgoMentor AI — recommendation service.

Contains the static problem bank, the scoring function that ranks
problems according to the student's daily context, and the helper
that produces the human-readable plan note.

All scoring logic is kept identical to the original monolith so that
every existing test assertion and expected match_score continues to hold.
"""

from app.models import Goal, Situation, Workload


# ============================================================
# Temporary Problem Bank
# Later this will come from Supabase.
# ============================================================

PROBLEM_BANK: list[dict] = [
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
# Scoring Logic
# ============================================================

def calculate_match_score(
    problem: dict,
    workload: Workload,
    situation: Situation,
    weak_concept: str,
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
