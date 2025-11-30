"""Dependency providers for FastAPI routes."""

from fastapi import Request

from app.clients.ai4bharat import AI4BharatClient
from app.clients.revid import RevidClient
from app.core.config import Settings, get_settings
from app.services.job_store import JobStore


def get_settings_dependency() -> Settings:
    """Expose application settings for dependency injection."""

    return get_settings()


def get_job_store(request: Request) -> JobStore:
    """Return the job store instance attached to the FastAPI app."""

    return request.app.state.job_store


def get_ai4bharat_client(request: Request) -> AI4BharatClient:
    """Fetch the AI4Bharat client from the application state."""

    return request.app.state.ai4bharat_client


def get_revid_client(request: Request) -> RevidClient:
    """Fetch the Revid client from the application state."""

    return request.app.state.revid_client
