"""
AlgoMentor AI — database connection smoke test script.

Run this script manually after you have created backend/.env and filled in
your Supabase Session Pooler credentials.

Recommended (run from the backend/ folder):
    python -m scripts.check_database_connection

Alternative (also works from the backend/ folder):
    python scripts/check_database_connection.py

This script does NOT run automatically.  It is NOT part of the test suite.
It makes a real network connection to Supabase, so run it only once you have
created backend/.env with valid credentials.

NEVER commit backend/.env.
"""

import sys
import os

# Allow imports from the backend/ root when run as a script.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import get_settings
from app.database import check_database_connection


def main() -> None:
    settings = get_settings()

    if settings.storage_backend != "postgres":
        print(
            "Database connection not enabled. "
            "Set STORAGE_BACKEND=postgres in backend/.env first."
        )
        sys.exit(0)

    print("Attempting connection to Supabase PostgreSQL …")
    try:
        result = check_database_connection()
        print(
            f"Supabase PostgreSQL connection successful. "
            f"(database: {result['database']})"
        )
    except RuntimeError as exc:
        print(f"Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
