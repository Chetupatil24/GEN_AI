"""Application settings and configuration helpers."""

from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BanubaFilterConfig(BaseModel):
    """Represents a Banuba AR filter entry exposed to clients."""

    id: str
    name: str
    description: str


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # IndicTrans2 inference server configuration
    ai4bharat_base_url: str = "http://localhost:5000"
    ai4bharat_translate_path: str = "/translate"
    ai4bharat_api_key: Optional[str] = None

    revid_api_key: str = Field(default=...)
    revid_base_url: str = "https://api.revid.ai/v1"
    revid_create_job_path: str = "/videos"
    revid_status_path: str = "/videos/{job_id}"
    revid_result_path: str = "/videos/{job_id}/result"
    revid_webhook_secret: Optional[str] = None

    banuba_filters: List[BanubaFilterConfig] = Field(
        default_factory=lambda: [
            BanubaFilterConfig(
                id="desi-fire",
                name="Desi Fire",
                description="Adds spicy overlays and glow effects for dramatic roasts.",
            ),
            BanubaFilterConfig(
                id="pet-maharaja",
                name="Pet Maharaja",
                description="Turns pets into regal royalty with ornate accessories.",
            ),
            BanubaFilterConfig(
                id="bollywood-burn",
                name="Bollywood Burn",
                description="Provides cinematic lighting and spark particles.",
            ),
        ]
    )

    request_timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 1.5

    # Redis configuration for persistent job storage
    redis_url: str = "redis://localhost:6379/0"
    use_redis: bool = True
    redis_job_ttl_seconds: int = 86400 * 7  # 7 days

    # Backend webhook configuration (for notifying Railway backend)
    backend_webhook_url: Optional[str] = None  # Set to your Railway backend URL

    # CORS origins (add your Railway backend URL)
    cors_origins: List[str] = Field(
        default_factory=lambda: ["*"]  # In production, specify exact origins
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance for dependency injection."""

    return Settings()
