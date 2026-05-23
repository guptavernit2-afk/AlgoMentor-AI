"""
AlgoMentor AI — Student Profile Repository.

Provides two implementations of the same interface:

    MemoryProfileRepository   → backed by the in-memory PROFILE_STORE dict.
    PostgresProfileRepository → backed by public.student_profiles in Supabase.

The correct implementation is chosen at runtime by `get_profile_repository()`,
which reads `settings.storage_backend`.  The database engine is never created
until a Postgres operation is actually requested — importing this module is
always safe, even when no .env is present.
"""

from __future__ import annotations

import functools
from typing import Protocol

from sqlalchemy import text

from app.models import StudentProfile


# ============================================================
# Shared interface (structural, via Protocol)
# ============================================================

class ProfileRepositoryProtocol(Protocol):
    def save_profile(self, user_id: str, profile: StudentProfile) -> StudentProfile: ...
    def get_profile(self, user_id: str) -> StudentProfile | None: ...


# ============================================================
# Memory implementation
# ============================================================

class MemoryProfileRepository:
    """
    Stores profiles in the module-level PROFILE_STORE dictionary.

    This is the default in test environments and when STORAGE_BACKEND=memory.
    PROFILE_STORE is imported lazily to avoid circular imports.
    """

    @staticmethod
    def _store() -> dict:
        """Return PROFILE_STORE, imported on first access."""
        from app.storage import PROFILE_STORE  # noqa: PLC0415
        return PROFILE_STORE

    def save_profile(self, user_id: str, profile: StudentProfile) -> StudentProfile:
        self._store()[user_id] = profile
        return profile

    def get_profile(self, user_id: str) -> StudentProfile | None:
        return self._store().get(user_id)


# ============================================================
# PostgreSQL implementation
# ============================================================

class PostgresProfileRepository:
    """
    Persists profiles in public.student_profiles via SQLAlchemy Core text queries.

    No ORM model mapping is used — rows are read as plain dicts and converted
    into the existing Pydantic StudentProfile.

    The engine is obtained lazily from app.database.get_engine() at the moment
    of the first operation, not at class construction time.
    """

    # ---------------------------------------------------------------------------
    # Upsert statement (PostgreSQL 9.5+ ON CONFLICT … DO UPDATE)
    # ---------------------------------------------------------------------------
    _UPSERT_SQL = text("""
        INSERT INTO public.student_profiles (
            user_id,
            name,
            goal,
            current_topic,
            completed_topics,
            weak_concepts,
            preferred_study_time,
            minimum_daily_minutes,
            maximum_daily_minutes
        ) VALUES (
            :user_id,
            :name,
            :goal,
            :current_topic,
            :completed_topics,
            :weak_concepts,
            :preferred_study_time,
            :minimum_daily_minutes,
            :maximum_daily_minutes
        )
        ON CONFLICT (user_id) DO UPDATE SET
            name                  = EXCLUDED.name,
            goal                  = EXCLUDED.goal,
            current_topic         = EXCLUDED.current_topic,
            completed_topics      = EXCLUDED.completed_topics,
            weak_concepts         = EXCLUDED.weak_concepts,
            preferred_study_time  = EXCLUDED.preferred_study_time,
            minimum_daily_minutes = EXCLUDED.minimum_daily_minutes,
            maximum_daily_minutes = EXCLUDED.maximum_daily_minutes
        -- updated_at is automatically refreshed by the set_updated_at() trigger.
    """)

    _SELECT_SQL = text("""
        SELECT
            name,
            goal,
            current_topic,
            completed_topics,
            weak_concepts,
            preferred_study_time,
            minimum_daily_minutes,
            maximum_daily_minutes
        FROM public.student_profiles
        WHERE user_id = :user_id
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
    # save_profile
    # ---------------------------------------------------------------------------

    def save_profile(self, user_id: str, profile: StudentProfile) -> StudentProfile:
        """
        Upsert the profile row.

        PostgreSQL arrays are passed as Python lists; psycopg 3 maps them to
        the text[] column type automatically when SQLAlchemy uses the psycopg
        dialect.
        """
        try:
            engine = self._engine()
            with engine.begin() as conn:
                conn.execute(
                    self._UPSERT_SQL,
                    {
                        "user_id": user_id,
                        "name": profile.name,
                        "goal": profile.goal,
                        "current_topic": profile.current_topic,
                        "completed_topics": list(profile.completed_topics),
                        "weak_concepts": list(profile.weak_concepts),
                        "preferred_study_time": profile.preferred_study_time,
                        "minimum_daily_minutes": profile.minimum_daily_minutes,
                        "maximum_daily_minutes": profile.maximum_daily_minutes,
                    },
                )
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while saving profile for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None
        return profile

    # ---------------------------------------------------------------------------
    # get_profile
    # ---------------------------------------------------------------------------

    def get_profile(self, user_id: str) -> StudentProfile | None:
        """
        Fetch one profile row and convert it to StudentProfile.

        Returns None if no row exists (caller converts this to HTTP 404).
        Column values are mapped positionally to the Pydantic model.
        created_at / updated_at are intentionally excluded from the SELECT so
        they never appear in the API response, keeping backward compatibility.
        """
        try:
            engine = self._engine()
            with engine.connect() as conn:
                row = conn.execute(self._SELECT_SQL, {"user_id": user_id}).fetchone()
        except RuntimeError:
            raise
        except Exception as exc:
            raise RuntimeError(
                f"Database error while fetching profile for '{user_id}': "
                f"{type(exc).__name__}."
            ) from None

        if row is None:
            return None

        return StudentProfile(
            name=row.name,
            goal=row.goal,
            current_topic=row.current_topic,
            completed_topics=list(row.completed_topics),
            weak_concepts=list(row.weak_concepts),
            preferred_study_time=row.preferred_study_time,
            minimum_daily_minutes=row.minimum_daily_minutes,
            maximum_daily_minutes=row.maximum_daily_minutes,
        )


# ============================================================
# Factory / selector
# ============================================================

@functools.lru_cache(maxsize=1)
def get_profile_repository() -> MemoryProfileRepository | PostgresProfileRepository:
    """
    Return the appropriate ProfileRepository implementation.

    The selection is based on `settings.storage_backend`:
      "memory"   → MemoryProfileRepository  (default, always safe)
      "postgres" → PostgresProfileRepository (engine created lazily on first use)

    The result is cached so the same instance is reused across requests.
    No database connection is opened at selection time.
    """
    from app.config import get_settings  # local import keeps module load clean
    settings = get_settings()

    if settings.storage_backend == "postgres":
        return PostgresProfileRepository()
    return MemoryProfileRepository()
