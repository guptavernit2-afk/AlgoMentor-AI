"""
AlgoMentor AI — application factory.

Creates and configures the FastAPI instance, registers all routers,
and is the single source of truth for API metadata.
"""

from fastapi import FastAPI

from app.routers import (
    daily_overrides,
    daily_plans,
    general,
    profiles,
    recommendations,
    schedules,
)


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    application = FastAPI(
        title="AlgoMentor AI API",
        description="Backend API for the AlgoMentor AI DSA revision coach.",
        version="0.5.0",
    )

    application.include_router(general.router)
    application.include_router(profiles.router)
    application.include_router(schedules.router)
    application.include_router(daily_overrides.router)
    application.include_router(recommendations.router)
    application.include_router(daily_plans.router)

    return application


# Module-level app instance used by uvicorn / fastapi CLI.
app = create_app()
