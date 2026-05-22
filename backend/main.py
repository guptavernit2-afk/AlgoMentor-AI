from fastapi import FastAPI

app = FastAPI(
    title="AlgoMentor AI API",
    description="Backend API for the AlgoMentor AI DSA revision coach.",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Confirm that the backend server is running."""
    return {"message": "AlgoMentor AI backend is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health endpoint used to verify API availability."""
    return {"status": "healthy"}