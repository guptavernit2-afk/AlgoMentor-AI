"""
AlgoMentor AI — Student Profile service helpers.

Provides `require_profile(user_id)` as a single importable function that
works correctly in both storage modes:

  - memory   → reads from in-memory PROFILE_STORE via MemoryProfileRepository
  - postgres → reads from Supabase via PostgresProfileRepository

All routers and services that currently call `require_profile` continue to
import it from `app.storage` (which re-exports it from here) so no call site
changes are needed across the codebase.
"""

from fastapi import HTTPException

from app.models import StudentProfile
from app.repositories.profile_repository import get_profile_repository


def require_profile(user_id: str) -> StudentProfile:
    """
    Return the saved student profile for `user_id`, or raise HTTP 404.

    Delegates to whichever repository implementation is active
    (memory or postgres), determined once at startup by `get_profile_repository()`.

    This is the single authoritative guard used by:
      - GET  /api/users/{user_id}/profile
      - weekly schedule endpoints
      - daily override endpoints
      - SM-2 revision endpoints
      - daily plan endpoints
    """
    repo = get_profile_repository()
    profile = repo.get_profile(user_id)

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Student profile not found. Complete onboarding first.",
        )

    return profile
