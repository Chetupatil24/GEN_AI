"""Shared pytest fixtures for FastAPI endpoint tests."""

from __future__ import annotations

import itertools
from collections.abc import Generator
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import Settings, get_settings
from app.dependencies import (
    get_ai4bharat_client,
    get_job_store,
    get_revid_client,
    get_settings_dependency,
)
from app.main import app
from app.services.job_store import JobStore


class FakeAI4BharatClient:
    """Stubbed AI4Bharat client returning predictable translations."""

    async def translate_text(
        self,
        *,
        text: str,
        source_language: str | None = None,
        target_language: str = "en",
        task: str = "translation",
    ) -> Dict[str, Any]:
        return {
            "translated_text": f"{text} (translated to {target_language})",
            "source_language": source_language or "auto",
            "target_language": target_language,
            "task": task,
        }


class FakeRevidClient:
    """Stubbed Revid client that simulates async video jobs."""

    _id_iter = itertools.count(1)

    def __init__(self) -> None:
        self._jobs: Dict[str, Dict[str, Any]] = {}

    async def create_video_job(self, *, text: str, image_url: str, language: str) -> Dict[str, Any]:
        job_id = f"job-{next(self._id_iter)}"
        self._jobs[job_id] = {
            "status": "queued",
            "text": text,
            "image_url": image_url,
            "language": language,
            "video_url": None,
        }
        return {"job_id": job_id, "status": "queued", "detail": None}

    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        job = self._jobs[job_id]
        job["status"] = "completed"
        job["video_url"] = f"https://cdn.example.com/{job_id}.mp4"
        return {"status": job["status"], "video_url": job["video_url"], "detail": "done"}

    async def get_job_result(self, job_id: str) -> Dict[str, Any]:
        job = self._jobs[job_id]
        return {"video_url": job["video_url"]}


@pytest.fixture
def job_store() -> JobStore:
    return JobStore()


@pytest.fixture
def fake_ai4bharat_client() -> FakeAI4BharatClient:
    return FakeAI4BharatClient()


@pytest.fixture
def fake_revid_client() -> FakeRevidClient:
    return FakeRevidClient()


@pytest.fixture
def client(
    job_store: JobStore,
    fake_ai4bharat_client: FakeAI4BharatClient,
    fake_revid_client: FakeRevidClient,
) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_job_store] = lambda: job_store
    app.dependency_overrides[get_ai4bharat_client] = lambda: fake_ai4bharat_client
    app.dependency_overrides[get_revid_client] = lambda: fake_revid_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def settings_override() -> Generator[Settings, None, None]:
    """Fixture that clears the settings cache and provides fresh settings."""
    get_settings.cache_clear()
    yield get_settings()
    get_settings.cache_clear()
