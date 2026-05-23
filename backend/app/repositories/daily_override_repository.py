"""
AlgoMentor AI — Daily Override Repository.

Provides two implementations of the same interface:

    MemoryDailyOverrideRepository   → backed by the in-memory DAILY_OVERRIDE_STORE.
    PostgresDailyOverrideRepository → backed by public.daily_overrides in Supabase.

The correct implementation is chosen at runtime by `get_daily_override_repository()`,
which reads `settings.storage_backend`.  The database engine is never created
until a Postgres operation is actually requested — importing this module is
always safe, even when no .env is present.

Schema note:
    public.daily_overrides has a UNIQUE constraint on (user_id, override_date)
    and a foreign key to public.student_profiles(user_id) ON DELETE CASCADE.
    One row per user per date.
"""

from __future__ import annotations

import functools
from datetime import date as Date
from typing import Protocol

from sqlalchemy import text

from app.models import DailyOverride


# ============================================================
# Shared interface (structural, via Protocol)
# ============================================================

class DailyOverrideRepositoryProtocol(Protocol):
    def save_override(
        self, user_id: str, override_date: Date, override: DailyOverride
    ) -> DailyOverride: ...

    def get_override(
        self, user_id: str, override_date: Date
    ) -> DailyOverride | None: ...

    def delete_override(
        self, user_id: str, override_date: Date
    ) -> bool: ...


# ============================================================
# Memory implementation
# ============================================================

class MemoryDailyOverrideRepository:
    """
    Stores daily overrides in the module-level DAILY_OVERRIDE_STORE dictionary.

    Keys are (user_id, override_date) tuples.
    This is the default in test environments and when STORAGE_BACKEND=memory.
    DAILY_OVERRIDE_STORE is imported lazily to avoid circular imports.
    """

    @staticmethod
    def _store() -> dict:
        """Return DAILY_OVERRIDE_STORE, imported on first access."""
        from app.storage import DAILY_OVERRIDE_STORE  # noqa: PLC0415
        return DAILY_OVERRIDE_STORE

    def save_override(
        self, user_id: str, override_date: Date, override: DailyOverride
    ) -> DailyOverride:
        self._store()[(user_id, override_date)] = override
        return override

    def get_override(
        self, user_id: str, override_date: Date
    ) -> DailyOverride | None:
        return self._store().get((user_id, override_date))

    def delete_override(
        self, user_id: str, override_date: Date
    ) -> bool:
        store = self._store()
        key = (user_id, override_date)
        if key not in store:
            return False
        del store[key]
        return True


# ============================================================
# PostgreSQL implementation
# ============================================================

class PostgresDailyOverrideRepository:
    """
    Persists daily overrides in public.daily_overrides via SQLAlchemy Core.

    Upserts are keyed by (user_id, override_date); the unique constraint in
    Supabase prevents duplicates.  The engine is obtained lazily from
    app.database.get_engine() at the moment of the first operation.
    """

    # ---------------------------------------------------------------------------
    # SQL statements
    # ---------------------------------------------------------------------------

    _UPSERT_SQL = text("""
        INSERT INTO public.daily_overrides (
            user_id,
            override_date,
            situation,
            extra_available_minutes,
            energy_level,
            note
        ) VALUES (
            :user_id,
            :override_date,
            :situation,
            :extra_available_minutes,
            :energy_level,
            :note
        )
        ON CONFLICT (user_id, override_date) DO UPDATE SET
            situation               = EXCLUDED.situation,
            extra_available_minutes = EXCLUDED.extra_available_minutes,
            energy_level            = EXCLUDED.energy_level,
            note                    = EXCLUDED.note
        -- updated_at is refreshed automatically by the set_updated_at() trigger.
    """)

    _SELECT_SQL = text("""
        SELECT
            situation,
            extra_available_minutes,
            energy_level,
            note
        FROM public.daily_overrides
        WHERE user_id = :user_id
          AND override_date = :override_date
    """)

    _DELETE_SQL = text("""
        DELETE FROM public.daily_overrides
        WHERE user_id      = :user_id
          AND override_date = :override_date
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
    # save_override
    # ---------------------------------------------------------------------------

    def save_override(
        self, user_id: str, override_date: Date, override: DailyOverride
    ) -> DailyOverride:
        """
        Upsert the daily override row.

        On conflict the row is updated; on insert a new row is created.
        The updated_at column is refreshed by the database trigger.
        """
        try:
            engine = self._engine()
            with engine.begin() as conn:
                conn.execute(
                    self._UPSERT_SQL,
                    {
                        "user_id": user_id,
                        "override_date": override_date,
                        "situation": override.situation,
                        "extra_available_minutes": override.extra_available_minutes,
                        "energy_level": override.energy_level,
                        "note": override.note,
                    },
                )
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while saving daily override for '{user_id}' "
                f"on {override_date}: {type(exc).__name__}."
            ) from None
        return override

    # ---------------------------------------------------------------------------
    # get_override
    # ---------------------------------------------------------------------------

    def get_override(
        self, user_id: str, override_date: Date
    ) -> DailyOverride | None:
        """
        Fetch the daily override row for (user_id, override_date).

        Returns None if no row exists.
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                row = conn.execute(
                    self._SELECT_SQL,
                    {"user_id": user_id, "override_date": override_date},
                ).fetchone()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while fetching daily override for '{user_id}' "
                f"on {override_date}: {type(exc).__name__}."
            ) from None

        if row is None:
            return None

        return DailyOverride(
            situation=row.situation,
            extra_available_minutes=row.extra_available_minutes,
            energy_level=row.energy_level,
            note=row.note,
        )

    # ---------------------------------------------------------------------------
    # delete_override
    # ---------------------------------------------------------------------------

    def delete_override(
        self, user_id: str, override_date: Date
    ) -> bool:
        """
        Delete the daily override row for (user_id, override_date).

        Returns True if a row was deleted, False if none matched.
        Never deletes the parent profile or weekly schedule.
        """
        try:
            engine = self._engine()
            with engine.begin() as conn:
                result = conn.execute(
                    self._DELETE_SQL,
                    {"user_id": user_id, "override_date": override_date},
                )
                deleted_count = result.rowcount
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while deleting daily override for '{user_id}' "
                f"on {override_date}: {type(exc).__name__}."
            ) from None

        return deleted_count > 0


# ============================================================
# Factory / selector
# ============================================================

@functools.lru_cache(maxsize=1)
def get_daily_override_repository() -> (
    MemoryDailyOverrideRepository | PostgresDailyOverrideRepository
):
    """
    Return the appropriate DailyOverrideRepository implementation.

    The selection is based on `settings.storage_backend`:
      "memory"   → MemoryDailyOverrideRepository  (default, always safe)
      "postgres" → PostgresDailyOverrideRepository (engine created lazily)

    The result is cached so the same instance is reused across requests.
    No database connection is opened at selection time.
    """
    from app.config import get_settings  # local import keeps module load clean
    settings = get_settings()

    if settings.storage_backend == "postgres":
        return PostgresDailyOverrideRepository()
    return MemoryDailyOverrideRepository()
