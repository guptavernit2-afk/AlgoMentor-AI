"""
AlgoMentor AI — SM-2 Revision Repository.

Provides two implementations of the same interface:

    MemoryRevisionRepository   → backed by REVISION_STATE_STORE and REVISION_HISTORY_STORE.
    PostgresRevisionRepository → backed by public.topic_revision_states and
                                  public.topic_review_history in Supabase.

The correct implementation is chosen at runtime by `get_revision_repository()`,
which reads `settings.storage_backend`.  The database engine is never created
until a Postgres operation is actually requested — importing this module is
always safe, even when no .env is present.

ATOMIC WRITE GUARANTEE (Postgres mode):
    Recording one review produces two database effects:
      1. Upsert into public.topic_revision_states  (current state).
      2. Insert into public.topic_review_history   (immutable audit row).
    Both writes share a single `engine.begin()` transaction.  If either
    fails, the entire transaction rolls back, so state and history are
    always mutually consistent.

Schema notes:
    topic_revision_states: UNIQUE(user_id, topic)
    topic_review_history:  append-only, no updated_at trigger by design
    Both tables FK to student_profiles(user_id) ON DELETE CASCADE
"""

from __future__ import annotations

import functools
from datetime import date as Date
from typing import Protocol

from sqlalchemy import text

from app.models import TopicReviewRecord, TopicRevisionState


# ============================================================
# Shared interface (structural, via Protocol)
# ============================================================

class RevisionRepositoryProtocol(Protocol):
    def get_state(self, user_id: str, topic: str) -> TopicRevisionState | None: ...

    def save_review_result(
        self,
        user_id: str,
        state: TopicRevisionState,
        record: TopicReviewRecord,
    ) -> TopicRevisionState: ...

    def list_states(self, user_id: str) -> list[TopicRevisionState]: ...

    def list_history(self, user_id: str) -> list[TopicReviewRecord]: ...


# ============================================================
# Memory implementation
# ============================================================

class MemoryRevisionRepository:
    """
    Stores SM-2 state and history in the module-level in-memory dictionaries.

    State  key: (user_id, normalised_topic_name)  → TopicRevisionState
    History key: user_id → list[TopicReviewRecord]  (chronological append)

    Both stores are imported lazily to avoid circular imports.
    """

    # ----- internal helpers -----

    @staticmethod
    def _state_store() -> dict:
        from app.storage import REVISION_STATE_STORE  # noqa: PLC0415
        return REVISION_STATE_STORE

    @staticmethod
    def _history_store() -> dict:
        from app.storage import REVISION_HISTORY_STORE  # noqa: PLC0415
        return REVISION_HISTORY_STORE

    @staticmethod
    def _norm(topic: str) -> str:
        return topic.strip().lower()

    # ----- public interface -----

    def get_state(self, user_id: str, topic: str) -> TopicRevisionState | None:
        """Return current SM-2 state for the canonical topic, or None."""
        key = (user_id, self._norm(topic))
        return self._state_store().get(key)

    def save_review_result(
        self,
        user_id: str,
        state: TopicRevisionState,
        record: TopicReviewRecord,
    ) -> TopicRevisionState:
        """
        Persist new SM-2 state and append the review record atomically
        (in memory this is always atomic since both writes are in-process).
        """
        key = (user_id, self._norm(state.topic))
        self._state_store()[key] = state
        self._history_store().setdefault(user_id, []).append(record)
        return state

    def list_states(self, user_id: str) -> list[TopicRevisionState]:
        """Return all tracked topic states for the user (unordered)."""
        return [
            state
            for (uid, _), state in self._state_store().items()
            if uid == user_id
        ]

    def list_history(self, user_id: str) -> list[TopicReviewRecord]:
        """
        Return all review records in insertion (chronological) order.
        Memory mode preserves insertion order via list.append().
        """
        return list(self._history_store().get(user_id, []))


# ============================================================
# PostgreSQL implementation
# ============================================================

class PostgresRevisionRepository:
    """
    Persists SM-2 revision state and history in Supabase via SQLAlchemy Core.

    All writes happen inside a single database transaction.  The engine is
    obtained lazily from app.database.get_engine() only when an operation
    is first requested, not at import or construction time.
    """

    # ---------------------------------------------------------------------------
    # SQL statements
    # ---------------------------------------------------------------------------

    # Upsert current state; conflict target (user_id, topic)
    _UPSERT_STATE_SQL = text("""
        INSERT INTO public.topic_revision_states (
            user_id,
            topic,
            repetitions,
            interval_days,
            easiness_factor,
            last_quality,
            last_reviewed_on,
            next_review_date,
            total_reviews
        ) VALUES (
            :user_id,
            :topic,
            :repetitions,
            :interval_days,
            :easiness_factor,
            :last_quality,
            :last_reviewed_on,
            :next_review_date,
            :total_reviews
        )
        ON CONFLICT (user_id, topic) DO UPDATE SET
            repetitions      = EXCLUDED.repetitions,
            interval_days    = EXCLUDED.interval_days,
            easiness_factor  = EXCLUDED.easiness_factor,
            last_quality     = EXCLUDED.last_quality,
            last_reviewed_on = EXCLUDED.last_reviewed_on,
            next_review_date = EXCLUDED.next_review_date,
            total_reviews    = EXCLUDED.total_reviews
        -- updated_at is refreshed automatically by the set_updated_at() trigger.
        -- created_at is NOT touched on conflict.
    """)

    # Append-only history insert (no ON CONFLICT — every review is a new row)
    _INSERT_HISTORY_SQL = text("""
        INSERT INTO public.topic_review_history (
            user_id,
            topic,
            quality,
            reviewed_on,
            interval_days_after_review,
            easiness_factor_after_review,
            next_review_date
        ) VALUES (
            :user_id,
            :topic,
            :quality,
            :reviewed_on,
            :interval_days_after_review,
            :easiness_factor_after_review,
            :next_review_date
        )
    """)

    # Fetch one topic state
    _SELECT_STATE_SQL = text("""
        SELECT
            topic,
            repetitions,
            interval_days,
            easiness_factor,
            last_quality,
            last_reviewed_on,
            next_review_date,
            total_reviews
        FROM public.topic_revision_states
        WHERE user_id = :user_id
          AND topic   = :topic
    """)

    # Fetch all topic states for user
    _SELECT_ALL_STATES_SQL = text("""
        SELECT
            topic,
            repetitions,
            interval_days,
            easiness_factor,
            last_quality,
            last_reviewed_on,
            next_review_date,
            total_reviews
        FROM public.topic_revision_states
        WHERE user_id = :user_id
    """)

    # Fetch history in chronological (insertion) order
    # Use id ASC to mirror the list.append() order from memory mode.
    _SELECT_HISTORY_SQL = text("""
        SELECT
            topic,
            quality,
            reviewed_on,
            interval_days_after_review,
            easiness_factor_after_review,
            next_review_date
        FROM public.topic_review_history
        WHERE user_id = :user_id
        ORDER BY id ASC
    """)

    # ---------------------------------------------------------------------------
    # Engine accessor (lazy)
    # ---------------------------------------------------------------------------

    @staticmethod
    def _engine():
        """Return the SQLAlchemy engine; raises RuntimeError if misconfigured."""
        from app.database import get_engine  # local import avoids circular refs
        return get_engine()

    # ---------------------------------------------------------------------------
    # get_state
    # ---------------------------------------------------------------------------

    def get_state(self, user_id: str, topic: str) -> TopicRevisionState | None:
        """
        Fetch the canonical state row for (user_id, topic).

        The `topic` argument must already be the canonical form (as stored in
        the DB and returned by _resolve_canonical_topic).  Returns None if no
        row exists (first review of this topic).
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                row = conn.execute(
                    self._SELECT_STATE_SQL,
                    {"user_id": user_id, "topic": topic},
                ).fetchone()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while fetching revision state for '{user_id}' / "
                f"topic '{topic}': {type(exc).__name__}."
            ) from None

        if row is None:
            return None

        return TopicRevisionState(
            topic=row.topic,
            repetitions=row.repetitions,
            interval_days=row.interval_days,
            easiness_factor=float(row.easiness_factor),
            last_quality=row.last_quality,
            last_reviewed_on=row.last_reviewed_on,
            next_review_date=row.next_review_date,
            total_reviews=row.total_reviews,
        )

    # ---------------------------------------------------------------------------
    # save_review_result — atomic state upsert + history insert
    # ---------------------------------------------------------------------------

    def save_review_result(
        self,
        user_id: str,
        state: TopicRevisionState,
        record: TopicReviewRecord,
    ) -> TopicRevisionState:
        """
        Atomically upsert the current topic state and append a history record.

        Both operations share one `engine.begin()` transaction.  If either
        statement fails the whole transaction rolls back — partial writes are
        impossible.
        """
        try:
            engine = self._engine()
            with engine.begin() as conn:
                # 1. Upsert current state
                conn.execute(
                    self._UPSERT_STATE_SQL,
                    {
                        "user_id": user_id,
                        "topic": state.topic,
                        "repetitions": state.repetitions,
                        "interval_days": state.interval_days,
                        "easiness_factor": state.easiness_factor,
                        "last_quality": state.last_quality,
                        "last_reviewed_on": state.last_reviewed_on,
                        "next_review_date": state.next_review_date,
                        "total_reviews": state.total_reviews,
                    },
                )

                # 2. Append audit record (must be inside same transaction)
                conn.execute(
                    self._INSERT_HISTORY_SQL,
                    {
                        "user_id": user_id,
                        "topic": record.topic,
                        "quality": record.quality,
                        "reviewed_on": record.reviewed_on,
                        "interval_days_after_review": record.interval_days_after_review,
                        "easiness_factor_after_review": record.easiness_factor_after_review,
                        "next_review_date": record.next_review_date,
                    },
                )
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while saving review result for '{user_id}' / "
                f"topic '{state.topic}': {type(exc).__name__}."
            ) from None

        return state

    # ---------------------------------------------------------------------------
    # list_states
    # ---------------------------------------------------------------------------

    def list_states(self, user_id: str) -> list[TopicRevisionState]:
        """
        Return all current topic states for the user.

        Sorting (due/upcoming) is handled by the SM-2 service layer,
        not here — consistent with memory mode behaviour.
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                rows = conn.execute(
                    self._SELECT_ALL_STATES_SQL,
                    {"user_id": user_id},
                ).fetchall()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while listing revision states for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None

        return [
            TopicRevisionState(
                topic=row.topic,
                repetitions=row.repetitions,
                interval_days=row.interval_days,
                easiness_factor=float(row.easiness_factor),
                last_quality=row.last_quality,
                last_reviewed_on=row.last_reviewed_on,
                next_review_date=row.next_review_date,
                total_reviews=row.total_reviews,
            )
            for row in rows
        ]

    # ---------------------------------------------------------------------------
    # list_history
    # ---------------------------------------------------------------------------

    def list_history(self, user_id: str) -> list[TopicReviewRecord]:
        """
        Return all review history records in chronological (insertion) order.

        Uses `ORDER BY id ASC` to match the list.append() order from memory mode,
        ensuring GET /revision-history returns records oldest-first in both modes.
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                rows = conn.execute(
                    self._SELECT_HISTORY_SQL,
                    {"user_id": user_id},
                ).fetchall()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while listing revision history for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None

        return [
            TopicReviewRecord(
                topic=row.topic,
                quality=row.quality,
                reviewed_on=row.reviewed_on,
                interval_days_after_review=row.interval_days_after_review,
                easiness_factor_after_review=float(row.easiness_factor_after_review),
                next_review_date=row.next_review_date,
            )
            for row in rows
        ]


# ============================================================
# Factory / selector
# ============================================================

@functools.lru_cache(maxsize=1)
def get_revision_repository() -> MemoryRevisionRepository | PostgresRevisionRepository:
    """
    Return the appropriate RevisionRepository implementation.

    The selection is based on `settings.storage_backend`:
      "memory"   → MemoryRevisionRepository   (default, always safe)
      "postgres" → PostgresRevisionRepository  (engine created lazily on first use)

    The result is cached so the same instance is reused across requests.
    No database connection is opened at selection time.
    """
    from app.config import get_settings  # local import keeps module load clean
    settings = get_settings()

    if settings.storage_backend == "postgres":
        return PostgresRevisionRepository()
    return MemoryRevisionRepository()
