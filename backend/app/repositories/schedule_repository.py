"""
AlgoMentor AI — Weekly Schedule Repository.

Provides two implementations of the same interface:

    MemoryScheduleRepository   → backed by the in-memory SCHEDULE_STORE dict.
    PostgresScheduleRepository → backed by public.weekly_schedules in Supabase.

The correct implementation is chosen at runtime by `get_schedule_repository()`,
which reads `settings.storage_backend`.  The database engine is never created
until a Postgres operation is actually requested — importing this module is
always safe, even when no .env is present.

Schema note:
    public.weekly_schedules has a UNIQUE constraint on (user_id, day_name)
    and a foreign key to public.student_profiles(user_id).
    Seven rows per user — one per weekday.
"""

from __future__ import annotations

import functools
import json
from typing import Protocol

from sqlalchemy import text

from app.models import ClassSlot, DaySchedule, WeeklySchedule


# Canonical weekday order used for result ordering
_DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# ============================================================
# Shared interface (structural, via Protocol)
# ============================================================

class ScheduleRepositoryProtocol(Protocol):
    def save_schedule(self, user_id: str, schedule: WeeklySchedule) -> WeeklySchedule: ...
    def get_schedule(self, user_id: str) -> WeeklySchedule | None: ...


# ============================================================
# Memory implementation
# ============================================================

class MemoryScheduleRepository:
    """
    Stores weekly schedules in the module-level SCHEDULE_STORE dictionary.

    This is the default in test environments and when STORAGE_BACKEND=memory.
    SCHEDULE_STORE is imported lazily to avoid circular imports.
    """

    @staticmethod
    def _store() -> dict:
        """Return SCHEDULE_STORE, imported on first access."""
        from app.storage import SCHEDULE_STORE  # noqa: PLC0415
        return SCHEDULE_STORE

    def save_schedule(self, user_id: str, schedule: WeeklySchedule) -> WeeklySchedule:
        self._store()[user_id] = schedule
        return schedule

    def get_schedule(self, user_id: str) -> WeeklySchedule | None:
        return self._store().get(user_id)


# ============================================================
# PostgreSQL implementation
# ============================================================

class PostgresScheduleRepository:
    """
    Persists weekly schedules in public.weekly_schedules via SQLAlchemy Core.

    Each save atomically upserts all seven weekday rows inside a single
    database transaction.  A partial save is rolled back automatically.

    The engine is obtained lazily from app.database.get_engine() at the
    moment of the first operation, not at class construction time.
    """

    # ---------------------------------------------------------------------------
    # SQL statements
    # ---------------------------------------------------------------------------

    # Upsert one weekday row; conflict on (user_id, day_name).
    _UPSERT_DAY_SQL = text("""
        INSERT INTO public.weekly_schedules (
            user_id,
            day_name,
            is_free_day,
            classes
        ) VALUES (
            :user_id,
            :day_name,
            :is_free_day,
            :classes
        )
        ON CONFLICT (user_id, day_name) DO UPDATE SET
            is_free_day = EXCLUDED.is_free_day,
            classes     = EXCLUDED.classes
        -- updated_at is refreshed automatically by the set_updated_at() trigger.
    """)

    _SELECT_ALL_DAYS_SQL = text("""
        SELECT
            day_name,
            is_free_day,
            classes
        FROM public.weekly_schedules
        WHERE user_id = :user_id
        ORDER BY
            CASE day_name
                WHEN 'Monday'    THEN 1
                WHEN 'Tuesday'   THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday'  THEN 4
                WHEN 'Friday'    THEN 5
                WHEN 'Saturday'  THEN 6
                WHEN 'Sunday'    THEN 7
                ELSE 8
            END
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
    # save_schedule — atomic seven-day upsert
    # ---------------------------------------------------------------------------

    def save_schedule(self, user_id: str, schedule: WeeklySchedule) -> WeeklySchedule:
        """
        Upsert all seven weekday rows inside a single database transaction.

        If any row fails, the entire transaction is rolled back, preventing a
        half-saved schedule from being persisted.

        classes is serialised as a JSONB array of objects:
            [{"title": "...", "start_time": "HH:MM", "end_time": "HH:MM"}, ...]
        """
        try:
            engine = self._engine()
            with engine.begin() as conn:  # begin() auto-commits or rolls back
                for day in schedule.days:
                    classes_json = json.dumps(
                        [
                            {
                                "title": slot.title,
                                "start_time": slot.start_time,
                                "end_time": slot.end_time,
                            }
                            for slot in day.classes
                        ]
                    )
                    conn.execute(
                        self._UPSERT_DAY_SQL,
                        {
                            "user_id": user_id,
                            "day_name": day.day,
                            "is_free_day": day.is_free_day,
                            "classes": classes_json,
                        },
                    )
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while saving weekly schedule for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None
        return schedule

    # ---------------------------------------------------------------------------
    # get_schedule — read and reconstruct WeeklySchedule
    # ---------------------------------------------------------------------------

    def get_schedule(self, user_id: str) -> WeeklySchedule | None:
        """
        Fetch all seven weekday rows and convert them to WeeklySchedule.

        Returns None if no rows exist for the user.

        Raises RuntimeError if fewer than seven rows exist (incomplete data),
        rather than returning a broken partial schedule.

        The CASE expression in the SQL guarantees Monday-to-Sunday ordering
        even if the database returns rows in a different physical order.
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                rows = conn.execute(
                    self._SELECT_ALL_DAYS_SQL, {"user_id": user_id}
                ).fetchall()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while fetching weekly schedule for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None

        if not rows:
            return None

        if len(rows) < 7:
            raise RuntimeError(
                f"Incomplete weekly schedule data for '{user_id}': "
                f"expected 7 days, found {len(rows)}. "
                "The schedule may have been partially written. "
                "Re-save the full seven-day schedule to fix this."
            )

        day_schedules: list[DaySchedule] = []
        for row in rows:
            # classes is returned from psycopg as a Python list of dicts
            # (psycopg 3 deserialises JSONB automatically).
            raw_classes = row.classes if row.classes is not None else []
            if isinstance(raw_classes, str):
                # Defensive fallback: parse if returned as a raw JSON string
                raw_classes = json.loads(raw_classes)

            class_slots = [
                ClassSlot(
                    title=c["title"],
                    start_time=c["start_time"],
                    end_time=c["end_time"],
                )
                for c in raw_classes
            ]

            day_schedules.append(
                DaySchedule(
                    day=row.day_name,
                    is_free_day=row.is_free_day,
                    classes=class_slots,
                )
            )

        return WeeklySchedule(days=day_schedules)


# ============================================================
# Factory / selector
# ============================================================

@functools.lru_cache(maxsize=1)
def get_schedule_repository() -> MemoryScheduleRepository | PostgresScheduleRepository:
    """
    Return the appropriate ScheduleRepository implementation.

    The selection is based on `settings.storage_backend`:
      "memory"   → MemoryScheduleRepository  (default, always safe)
      "postgres" → PostgresScheduleRepository (engine created lazily on first use)

    The result is cached so the same instance is reused across requests.
    No database connection is opened at selection time.
    """
    from app.config import get_settings  # local import keeps module load clean
    settings = get_settings()

    if settings.storage_backend == "postgres":
        return PostgresScheduleRepository()
    return MemoryScheduleRepository()
