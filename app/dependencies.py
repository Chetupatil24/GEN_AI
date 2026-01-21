"""Dependency providers for FastAPI routes."""

from typing import Optional

from fastapi import Request

from app.clients.ai4bharat import AI4BharatClient
from app.clients.fal import FalClient
from app.clients.pets_backend import PetsBackendClient
from app.core.config import Settings, get_settings
from app.services.job_store import JobStore
from app.services.video_storage import VideoStorageService


def get_settings_dependency() -> Settings:
    """Expose application settings for dependency injection."""

    return get_settings()


def get_job_store(request: Request) -> JobStore:
    """Return the job store instance attached to the FastAPI app."""

    return request.app.state.job_store


def get_ai4bharat_client(request: Request) -> AI4BharatClient:
    """Fetch the AI4Bharat client from the application state."""

    return request.app.state.ai4bharat_client


def get_fal_client(request: Request) -> FalClient:
    """Fetch the fal.ai client from the application state."""

    return request.app.state.fal_client


def get_video_storage(request: Request) -> VideoStorageService:
    """Fetch the video storage service from the application state."""

    return request.app.state.video_storage


def get_pets_backend_client() -> Optional[PetsBackendClient]:
    """Get pets-backend client if enabled."""
    settings = get_settings()
    if not settings.pets_backend_enabled:
        return None
    return PetsBackendClient(base_url=settings.pets_backend_url)
