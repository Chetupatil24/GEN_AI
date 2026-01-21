"""Pydantic schemas for FastAPI request and response payloads."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.services.job_store import JobStatus

SUPPORTED_LANGUAGES = {"hi", "te", "ta", "ml", "bn", "gu", "mr", "pa", "en"}


class TranslateTextRequest(BaseModel):
    """Payload for submitting text to the AI4Bharat translation endpoint."""

    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: str = Field(..., description="ISO 639-1 code such as hi, te, ta, en.")
    target_lang: str = Field(
        default="en",
        description="Target language for translation; defaults to English.",
    )
    task: str = Field(
        default="translation",
        description="Inference mode, e.g. translation or sentiment-analysis.",
        max_length=64,
    )

    @field_validator("source_lang")
    def validate_source_language(cls, value: str) -> str:
        if value.lower() not in SUPPORTED_LANGUAGES:
            raise ValueError("Unsupported source language code.")
        return value.lower()

    @field_validator("target_lang")
    def validate_target_language(cls, value: str) -> str:
        return value.lower()


class TranslateTextResponse(BaseModel):
    """Response from the AI4Bharat translation endpoint."""

    translated_text: str
    source_language: str
    target_language: str
    task: str
    provider_metadata: Optional[Dict[str, Any]] = None


class GenerateVideoRequest(BaseModel):
    """Request body for submitting a new video generation job."""

    text: str = Field(..., min_length=1, max_length=5000)
    image_url: Optional[str] = None  # Changed from HttpUrl to str to accept data URLs
    image_data: Optional[str] = Field(None, description="Base64 encoded image data (data:image/...;base64,...)")
    
    @field_validator("image_data", mode="before")
    @classmethod
    def validate_image_data(cls, v):
        """Validate that either image_url or image_data is provided."""
        return v
    
    def model_post_init(self, __context):
        """Ensure either image_url or image_data is provided."""
        if not self.image_url and not self.image_data:
            raise ValueError("Either 'image_url' or 'image_data' must be provided")


class GenerateVideoResponse(BaseModel):
    """Response payload containing the queued job identifier."""

    job_id: str
    status: JobStatus


class VideoStatusResponse(BaseModel):
    """Represents the status of an asynchronous video job."""

    job_id: str
    status: JobStatus
    detail: Optional[str] = None
    updated_at: Optional[datetime] = None


class VideoResultResponse(BaseModel):
    """Contains the final video result location, if available."""

    job_id: str
    status: JobStatus
    video_url: Optional[str] = None
    detail: Optional[str] = None


class BanubaFilter(BaseModel):
    """Represents a Banuba AR filter exposed to the client."""

    id: str
    name: str
    description: str


class BanubaFiltersResponse(BaseModel):
    """Collection of Banuba filter descriptors."""

    filters: List[BanubaFilter]


class RevidWebhookEvent(BaseModel):
    """Incoming webhook payload from fal.ai (kept name for backwards compatibility)."""

    job_id: str
    status: JobStatus
    video_url: Optional[str] = None
    detail: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
