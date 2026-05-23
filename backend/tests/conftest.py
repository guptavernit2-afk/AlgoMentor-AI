"""
AlgoMentor AI — pytest configuration and test isolation.

WHY THIS FILE EXISTS
--------------------
`backend/app/config.py` uses pydantic-settings with `env_file=".env"`.
When pytest runs from `backend/`, the real local `.env` is found and loaded,
which may set `STORAGE_BACKEND=postgres`.  Without intervention, every test
that calls the profile API would use `PostgresProfileRepository` and write
real rows into the live Supabase `student_profiles` table.

This conftest enforces three layers of isolation:

  Layer 1 — os.environ override at module import time
    Set STORAGE_BACKEND=memory in os.environ before any test module is
    imported.  pydantic-settings reads os.environ with higher priority than
    the .env file, so the memory backend is selected regardless of .env
    content.

  Layer 2 — cache-clearing autouse fixture
    Clear get_settings() and get_profile_repository() LRU caches before and
    after every test so a test that patches these caches never pollutes a
    later test.

  Layer 3 — hard no-live-database guard
    Monkeypatch PostgresProfileRepository._engine() to raise AssertionError
    if called during the standard test suite.  Even if the repository class
    is accidentally selected, no connection will be attempted.

All three layers are session-scoped at the os.environ level and
per-test at the cache/store level.
"""

import os

# ============================================================
# Layer 1 — Force memory mode BEFORE any app module is imported.
#
# This runs at conftest import time, which is before pytest collects
# or imports test modules.  Because pydantic-settings treats os.environ
# values with higher priority than .env file values, this overrides
# whatever STORAGE_BACKEND=postgres is written in backend/.env.
# ============================================================
os.environ["STORAGE_BACKEND"] = "memory"

# Standard library imports only above this line.
# App imports below — they now see STORAGE_BACKEND=memory in os.environ.

import pytest


# ============================================================
# Layer 2 — Clear LRU caches and in-memory stores per test.
# ============================================================

@pytest.fixture(autouse=True)
def _reset_all_state():
    """
    Clear every cache and in-memory store before and after each test.

    - get_settings cache: ensures each test constructs a fresh Settings
      object that reads STORAGE_BACKEND from the current os.environ.
    - get_profile_repository cache: ensures the correct repository
      implementation is re-selected after any cache_clear in a test.
    - clear_all_stores: wipes the five in-memory dictionaries so no test
      leaks state (profile, schedule, overrides, SM-2 states, history).
    """
    from app.config import get_settings
    from app.repositories.profile_repository import get_profile_repository
    from app.repositories.schedule_repository import get_schedule_repository
    from app.repositories.daily_override_repository import get_daily_override_repository
    from app.storage import clear_all_stores

    # ---- setup ----
    get_settings.cache_clear()
    get_profile_repository.cache_clear()
    get_schedule_repository.cache_clear()
    get_daily_override_repository.cache_clear()
    clear_all_stores()

    yield

    # ---- teardown ----
    clear_all_stores()
    get_daily_override_repository.cache_clear()
    get_schedule_repository.cache_clear()
    get_profile_repository.cache_clear()
    get_settings.cache_clear()


# ============================================================
# Layer 3 — Hard no-live-database guard (autouse).
#
# PostgresProfileRepository._engine() is the single gateway through which
# any real database connection can be opened.  Replacing it with a function
# that raises AssertionError means a live connection is impossible during
# the standard test suite, even if a test accidentally constructs a
# PostgresProfileRepository.
#
# Tests that intentionally verify Postgres *repository selection* (not
# actual DB access) are not affected because they construct the repo object
# without calling _engine().
#
# Tests that explicitly patch app.database.get_engine with a MagicMock
# (e.g. test_postgres_save_error_does_not_leak_password) work correctly
# because this fixture patches the _engine() method on the class, not
# get_engine itself.  The mock in those tests replaces get_engine at a
# deeper level, so the AssertionError is never reached.
# ============================================================

@pytest.fixture(autouse=True)
def _block_live_db_engine(monkeypatch):
    """
    Replace all Postgres repository _engine() methods with a hard guard that
    raises AssertionError if called during automated tests.

    Covers:
      - PostgresProfileRepository._engine()
      - PostgresScheduleRepository._engine()
      - PostgresDailyOverrideRepository._engine()

    This is defence-in-depth on top of Layer 1:
    - Layer 1 prevents Postgres mode from being selected.
    - Layer 3 ensures that even if somehow selected, no connection is made.
    """
    def _forbidden_engine():
        raise AssertionError(
            "Live PostgreSQL access is forbidden during pytest. "
            "All tests must run in STORAGE_BACKEND=memory mode. "
            "If you need to test Postgres behaviour, use a MagicMock engine."
        )

    from app.repositories import profile_repository as profile_repo_module
    from app.repositories import schedule_repository as schedule_repo_module
    from app.repositories import daily_override_repository as override_repo_module

    monkeypatch.setattr(
        profile_repo_module.PostgresProfileRepository,
        "_engine",
        staticmethod(_forbidden_engine),
    )
    monkeypatch.setattr(
        schedule_repo_module.PostgresScheduleRepository,
        "_engine",
        staticmethod(_forbidden_engine),
    )
    monkeypatch.setattr(
        override_repo_module.PostgresDailyOverrideRepository,
        "_engine",
        staticmethod(_forbidden_engine),
    )
