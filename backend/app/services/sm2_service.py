"""
AlgoMentor AI — SM-2 spaced repetition service.

Implements the official SM-2 algorithm for topic-level revision scheduling.

SM-2 rules:
  - EF starts at 2.5; clamped to minimum 1.3.
  - quality 0-2  → reset repetitions, interval_days = 1.
  - quality >= 3 → rep 0→1 day, rep 1→6 days, rep ≥2 → ceil(prev_interval * prev_EF).
  - New EF = prev_EF + 0.1 - (5-q)*(0.08 + (5-q)*0.02), rounded to 2 dp.
  - next_review_date = reviewed_on + interval_days.

IMPORTANT: The previous EF is used when calculating the new interval, then
the EF is updated/stored.  This ordering is deterministic and tested.
"""

import math
from datetime import date as Date, timedelta

from fastapi import HTTPException

from app.models import (
    RevisionQueueResponse,
    StudentProfile,
    TopicReviewRecord,
    TopicReviewRequest,
    TopicRevisionState,
)
from app.storage import (
    REVISION_HISTORY_STORE,
    REVISION_STATE_STORE,
)


# ============================================================
# Constants
# ============================================================

_INITIAL_EF: float = 2.5
_MIN_EF: float = 1.3


# ============================================================
# Topic name normalisation
# ============================================================

def normalise_topic_name(topic: str) -> str:
    """Lower-case + strip for case-insensitive key matching."""
    return topic.strip().lower()


# ============================================================
# Topic validation
# ============================================================

def _resolve_canonical_topic(topic: str, profile: StudentProfile) -> str:
    """
    Return the profile's canonical capitalisation of `topic`, or raise
    HTTP 400 if the topic is not in completed_topics or current_topic.

    Matching is case-insensitive.
    """
    norm_request = normalise_topic_name(topic)

    # Check current_topic
    if normalise_topic_name(profile.current_topic) == norm_request:
        return profile.current_topic

    # Check completed_topics
    for ct in profile.completed_topics:
        if normalise_topic_name(ct) == norm_request:
            return ct

    raise HTTPException(
        status_code=400,
        detail=(
            "Topic must be present in the student's completed topics or "
            "current topic."
        ),
    )


# ============================================================
# Core SM-2 calculation
# ============================================================

def _new_ef(previous_ef: float, quality: int) -> float:
    """
    Update easiness factor using the SM-2 formula, clamped to >= 1.3
    and rounded to 2 decimal places.
    """
    updated = previous_ef + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    return round(max(_MIN_EF, updated), 2)


def calculate_sm2_update(
    previous_state: TopicRevisionState | None,
    topic: str,
    quality: int,
    reviewed_on: Date,
) -> TopicRevisionState:
    """
    Apply one SM-2 review cycle.

    Uses the *previous* easiness factor to derive the new interval, then
    calculates and stores the updated easiness factor.  The returned state
    object reflects the post-review values ready to be persisted.
    """
    # Pull previous values (or defaults for a brand-new topic)
    if previous_state is not None:
        prev_ef          = previous_state.easiness_factor
        prev_interval    = previous_state.interval_days
        prev_repetitions = previous_state.repetitions
        total_reviews    = previous_state.total_reviews + 1
    else:
        prev_ef          = _INITIAL_EF
        prev_interval    = 0
        prev_repetitions = 0
        total_reviews    = 1

    # --- Step 1: Calculate new interval using PREVIOUS EF ---
    if quality >= 3:
        if prev_repetitions == 0:
            new_interval = 1
        elif prev_repetitions == 1:
            new_interval = 6
        else:
            new_interval = math.ceil(prev_interval * prev_ef)
        new_repetitions = prev_repetitions + 1
    else:
        new_interval    = 1
        new_repetitions = 0

    # --- Step 2: Update EF using PREVIOUS EF ---
    new_ef_value = _new_ef(prev_ef, quality)

    # --- Step 3: Derive next review date ---
    next_review_date = reviewed_on + timedelta(days=new_interval)

    return TopicRevisionState(
        topic=topic,
        repetitions=new_repetitions,
        interval_days=new_interval,
        easiness_factor=new_ef_value,
        last_quality=quality,
        last_reviewed_on=reviewed_on,
        next_review_date=next_review_date,
        total_reviews=total_reviews,
    )


# ============================================================
# Review persistence
# ============================================================

def record_topic_review(
    user_id: str,
    profile: StudentProfile,
    request: TopicReviewRequest,
) -> TopicRevisionState:
    """
    Validate, compute, and persist one topic review.

    Returns the updated TopicRevisionState.
    """
    # Resolve canonical name (also validates against profile)
    canonical_topic = _resolve_canonical_topic(request.topic, profile)
    norm_key = (user_id, normalise_topic_name(canonical_topic))

    # Get previous state (None if first review)
    previous_state = REVISION_STATE_STORE.get(norm_key)

    # Calculate new SM-2 state
    new_state = calculate_sm2_update(
        previous_state=previous_state,
        topic=canonical_topic,
        quality=request.quality,
        reviewed_on=request.reviewed_on,
    )

    # Persist new state
    REVISION_STATE_STORE[norm_key] = new_state

    # Append audit record to history
    record = TopicReviewRecord(
        topic=canonical_topic,
        quality=request.quality,
        reviewed_on=request.reviewed_on,
        interval_days_after_review=new_state.interval_days,
        easiness_factor_after_review=new_state.easiness_factor,
        next_review_date=new_state.next_review_date,
    )
    REVISION_HISTORY_STORE.setdefault(user_id, []).append(record)

    return new_state


# ============================================================
# Revision queue
# ============================================================

def get_revision_queue(
    user_id: str,
    profile: StudentProfile,
    as_of_date: Date,
) -> RevisionQueueResponse:
    """
    Build a RevisionQueueResponse for the given date.

    due_topics      → next_review_date <= as_of_date, sorted most-overdue first.
    upcoming_topics → next_review_date > as_of_date, sorted soonest first.
    untracked_completed_topics → completed_topics with no SM-2 state yet.
    """
    # Gather all states belonging to this user
    tracked_states: list[TopicRevisionState] = []
    tracked_normalised: set[str] = set()

    for (uid, norm_topic), state in REVISION_STATE_STORE.items():
        if uid != user_id:
            continue
        tracked_normalised.add(norm_topic)

        delta = (as_of_date - state.next_review_date).days
        enriched = state.model_copy(
            update={
                "is_due": delta >= 0,
                "days_overdue": delta if delta >= 0 else None,
            }
        )
        tracked_states.append(enriched)

    # Split into due vs upcoming
    due_topics      = [s for s in tracked_states if s.is_due]
    upcoming_topics = [s for s in tracked_states if not s.is_due]

    # Sort due: most overdue first (largest days_overdue → earliest next_review_date)
    due_topics.sort(key=lambda s: s.next_review_date)

    # Sort upcoming: soonest next review first
    upcoming_topics.sort(key=lambda s: s.next_review_date)

    # Completed topics that have no SM-2 state yet
    untracked = [
        ct for ct in profile.completed_topics
        if normalise_topic_name(ct) not in tracked_normalised
    ]

    message = (
        "Revision topics are due today."
        if due_topics
        else "No tracked topics are due today."
    )

    return RevisionQueueResponse(
        user_id=user_id,
        as_of_date=as_of_date,
        due_topics=due_topics,
        upcoming_topics=upcoming_topics,
        untracked_completed_topics=untracked,
        message=message,
    )


# ============================================================
# Daily Plan integration helper
# ============================================================

def get_sm2_revision_focus(
    user_id: str,
    plan_date: Date,
) -> tuple[str | None, str]:
    """
    Return (revision_focus, revision_note) for the daily plan service.

    Cases:
      1. No SM-2 states at all for this user → fallback (None, fallback_note).
         The caller will use the profile's first completed topic as fallback.
      2. At least one due topic → use the most-overdue one.
      3. States exist but none are due → no forced focus; mention nearest date.
    """
    _FALLBACK_NOTE = (
        "Revision focus is currently derived from completed topics. "
        "SM-2 revision history will be integrated in the next phase."
    )

    # Collect all states for this user
    user_states = [
        state
        for (uid, _), state in REVISION_STATE_STORE.items()
        if uid == user_id
    ]

    if not user_states:
        # Case 1: no SM-2 history yet → use fallback
        return None, _FALLBACK_NOTE

    # Enrich with due information relative to plan_date
    due: list[TopicRevisionState] = []
    upcoming: list[TopicRevisionState] = []

    for state in user_states:
        delta = (plan_date - state.next_review_date).days
        if delta >= 0:
            enriched = state.model_copy(
                update={"is_due": True, "days_overdue": delta}
            )
            due.append(enriched)
        else:
            upcoming.append(state)

    if due:
        # Case 2: one or more topics are due → pick most overdue
        due.sort(key=lambda s: s.next_review_date)  # earliest date = most overdue
        most_overdue = due[0]
        note = (
            f"Revision focus selected from SM-2 due queue. "
            f"{most_overdue.topic} was due on "
            f"{most_overdue.next_review_date.isoformat()}."
        )
        return most_overdue.topic, note

    # Case 3: states exist but nothing is due yet
    upcoming.sort(key=lambda s: s.next_review_date)
    next_up = upcoming[0] if upcoming else None
    if next_up:
        note = (
            f"No tracked revision topics are due today. "
            f"Next scheduled review: {next_up.topic} on "
            f"{next_up.next_review_date.isoformat()}."
        )
    else:
        note = "No tracked revision topics are due today."

    return None, note
