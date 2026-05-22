"""
AlgoMentor AI — general / health endpoints.

GET /
GET /health
"""

from fastapi import APIRouter


router = APIRouter(tags=["General"])


@router.get("/")
def read_root() -> dict[str, str]:
    """Confirm that the backend server is running."""
    return {"message": "AlgoMentor AI backend is running"}


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health endpoint used to verify API availability."""
    return {"status": "healthy"}
