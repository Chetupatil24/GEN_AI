"""FastAPI application entry point for the pet roasting backend."""

import logging
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Remove invalid CORS_ORIGINS from environment before importing settings
if "CORS_ORIGINS" in os.environ:
    cors_val = os.environ["CORS_ORIGINS"]
    if cors_val in ["[*]", "[*", "*]", "*"]:
        os.environ.pop("CORS_ORIGINS", None)

from app.api.routes import router as api_router
from app.clients.ai4bharat import AI4BharatClient
from app.clients.fal import FalClient
from app.core.config import Settings, get_settings, clear_settings_cache
from app.services.job_store import JobStore
from app.services.redis_job_store import RedisJobStore
from app.services.video_storage import VideoStorageService

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown resources."""
    
    # Clear settings cache on startup to ensure fresh config
    clear_settings_cache()
    settings: Settings = get_settings()
    timeout = httpx.Timeout(settings.request_timeout_seconds)

    # Initialize job store (Redis or in-memory fallback)
    if settings.use_redis:
        try:
            job_store = RedisJobStore(
                redis_url=settings.redis_url,
                ttl_seconds=settings.redis_job_ttl_seconds
            )
            await job_store.connect()
            _logger.info("✅ Using Redis for persistent job storage")
        except Exception as e:
            _logger.warning(f"⚠️  Redis connection failed: {e}. Falling back to in-memory storage.")
            job_store = JobStore()
    else:
        _logger.info("Using in-memory job storage (not persistent)")
        job_store = JobStore()
    
    # Initialize video storage service
    video_storage = VideoStorageService(storage_path=settings.video_storage_path)

    async with httpx.AsyncClient(timeout=timeout) as async_client:
        ai4bharat_client = AI4BharatClient(
            http_client=async_client,
            base_url=settings.ai4bharat_base_url,
            translate_path=settings.ai4bharat_translate_path,
            api_key=settings.ai4bharat_api_key,
            max_retries=settings.max_retries,
            retry_backoff_factor=settings.retry_backoff_factor,
        )
        fal_client = FalClient(
            http_client=async_client,
            api_key=settings.fal_api_key,
            base_url=str(settings.fal_base_url),
            model_id=settings.fal_model_id,
            max_retries=settings.max_retries,
            retry_backoff_factor=settings.retry_backoff_factor,
        )

        app.state.settings = settings
        app.state.job_store = job_store
        app.state.ai4bharat_client = ai4bharat_client
        app.state.fal_client = fal_client
        app.state.video_storage = video_storage

        _logger.info("Application startup complete")
        yield

        # Cleanup
        if isinstance(job_store, RedisJobStore):
            await job_store.close()
        _logger.info("Application shutdown complete")


app = FastAPI(
    title="Pet Roast AI Backend",
    version="0.1.0",
    description="AI-powered pet roasting backend orchestrating multilingual NLP, video generation, and AR filters.",
    lifespan=lifespan,
)

# Configure CORS for Railway backend
settings_for_cors = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings_for_cors.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/healthz")
async def healthcheck() -> dict:
    """Simple readiness probe for container orchestrators."""

    return {"status": "ok"}

