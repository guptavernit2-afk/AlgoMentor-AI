"""
AlgoMentor AI — compatibility entry point.

Keeps the existing development command working without change:

    fastapi dev main.py
    uvicorn main:app --reload

All application logic lives under app/.
"""

from app.main import app  # noqa: F401  re-exported for CLI / uvicorn