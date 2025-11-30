"""Integration-style tests for the FastAPI routes with stubbed providers."""

from __future__ import annotations

import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.core.config import Settings


def test_translate_text_endpoint_returns_payload(client: TestClient) -> None:
    response = client.post(
        "/api/translate-text",
        json={"text": "Namaste dosto", "source_lang": "hi", "target_lang": "en"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["translated_text"].endswith("translated to en)")
    assert body["source_language"] == "hi"


def test_generate_video_flow(client: TestClient) -> None:
    payload = {
        "text": "Roast my pupper",
        "image_url": "https://cdn.example.com/pup.jpg",
    }
    create_response = client.post("/api/generate-video", json=payload)
    assert create_response.status_code == 202
    job = create_response.json()
    job_id = job["job_id"]

    status_resp = client.get(f"/api/video-status/{job_id}")
    assert status_resp.status_code == 200
    status_body = status_resp.json()
    assert status_body["status"] == "completed"

    result_resp = client.get(f"/api/video-result/{job_id}")
    assert result_resp.status_code == 200
    result_body = result_resp.json()
    assert result_body["video_url"].endswith(f"{job_id}.mp4")


def test_banuba_filters_list(client: TestClient) -> None:
    response = client.get("/api/banuba-filters")
    assert response.status_code == 200
    body = response.json()
    assert len(body["filters"]) >= 1
    assert {"id", "name", "description"}.issubset(body["filters"][0].keys())


def test_webhook_accepts_valid_signature(client: TestClient, settings_override, monkeypatch) -> None:
    """Test webhook endpoint accepts request with valid signature when secret is configured."""
    webhook_secret = "test-secret-key"
    monkeypatch.setenv("REVID_WEBHOOK_SECRET", webhook_secret)
    settings_override.revid_webhook_secret = webhook_secret

    payload = {
        "job_id": "test-job-123",
        "status": "completed",
        "video_url": "https://example.com/video.mp4",
        "detail": None,
        "extra": {},
    }
    # Compute signature on exactly what TestClient sends (compact JSON, no spaces)
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode("utf-8")
    signature = hmac.new(webhook_secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    response = client.post(
        "/api/revid-webhook",
        json=payload,
        headers={"X-Revid-Signature": f"sha256={signature}"},
    )
    assert response.status_code == 204


def test_webhook_rejects_invalid_signature(client: TestClient, settings_override, monkeypatch) -> None:
    """Test webhook endpoint rejects request with invalid signature when secret is configured."""
    webhook_secret = "test-secret-key"
    monkeypatch.setenv("REVID_WEBHOOK_SECRET", webhook_secret)
    settings_override.revid_webhook_secret = webhook_secret

    payload = {
        "job_id": "test-job-456",
        "status": "failed",
        "video_url": None,
        "detail": "Processing error",
        "extra": {},
    }

    response = client.post(
        "/api/revid-webhook",
        json=payload,
        headers={"X-Revid-Signature": "sha256=invalidsignature"},
    )
    assert response.status_code == 401
    assert "Invalid webhook signature" in response.json()["detail"]


def test_webhook_rejects_missing_signature(client: TestClient, settings_override, monkeypatch) -> None:
    """Test webhook endpoint rejects request without signature when secret is configured."""
    webhook_secret = "test-secret-key"
    monkeypatch.setenv("REVID_WEBHOOK_SECRET", webhook_secret)
    settings_override.revid_webhook_secret = webhook_secret

    payload = {
        "job_id": "test-job-789",
        "status": "completed",
        "video_url": "https://example.com/video2.mp4",
        "detail": None,
        "extra": {},
    }

    response = client.post("/api/revid-webhook", json=payload)
    assert response.status_code == 401
    assert "Missing webhook signature" in response.json()["detail"]


def test_webhook_works_without_secret(client: TestClient, monkeypatch) -> None:
    """Test webhook endpoint works without signature when secret is not configured (backward compatibility)."""
    # Temporarily unset the webhook secret to test backward compatibility
    monkeypatch.setenv("REVID_WEBHOOK_SECRET", "")

    from app.core.config import get_settings
    from app.dependencies import get_settings_dependency
    from app.main import app

    # Clear cache and override dependency with settings that have no webhook secret
    get_settings.cache_clear()
    test_settings = get_settings()
    app.dependency_overrides[get_settings_dependency] = lambda: test_settings

    try:
        payload = {
            "job_id": "test-job-000",
            "status": "completed",
            "video_url": "https://example.com/video3.mp4",
            "detail": None,
            "extra": {},
        }

        response = client.post("/api/revid-webhook", json=payload)
        assert response.status_code == 204
    finally:
        # Clean up
        if get_settings_dependency in app.dependency_overrides:
            del app.dependency_overrides[get_settings_dependency]
        get_settings.cache_clear()
