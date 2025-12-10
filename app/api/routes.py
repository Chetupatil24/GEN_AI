"""API route definitions for the pet roasting backend."""

import asyncio
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
import httpx

from app.clients.ai4bharat import AI4BharatClient
from app.clients.revid import RevidClient
from app.core.config import Settings
from app.core.exceptions import AI4BharatAPIError, RevidAPIError
from app.core.webhook import extract_signature_from_header, verify_webhook_signature
from app.dependencies import (
    get_ai4bharat_client,
    get_job_store,
    get_revid_client,
    get_settings_dependency,
)
from app.schemas import (
    BanubaFilter,
    BanubaFiltersResponse,
    TranslateTextRequest,
    TranslateTextResponse,
    GenerateVideoRequest,
    GenerateVideoResponse,
    RevidWebhookEvent,
    VideoResultResponse,
    VideoStatusResponse,
)
from app.services.job_store import JobRecord, JobStatus, JobStore
from app.services.pet_detection import get_pet_detector

router = APIRouter(prefix="/api")
_logger = logging.getLogger(__name__)

_STATUS_MAP: Dict[str, JobStatus] = {
    "queued": JobStatus.QUEUED,
    "pending": JobStatus.QUEUED,
    "processing": JobStatus.PROCESSING,
    "rendering": JobStatus.PROCESSING,
    "completed": JobStatus.COMPLETED,
    "success": JobStatus.COMPLETED,
    "failed": JobStatus.FAILED,
    "error": JobStatus.FAILED,
}


def _normalise_status(value: str) -> JobStatus:
    normalised = _STATUS_MAP.get(value.lower())
    return normalised if normalised else JobStatus.PROCESSING


def _extract_translated_text(result: Dict[str, Any]) -> str:
    candidates = (
        result.get("translated_text"),
        result.get("translation"),
        result.get("output_text"),
        result.get("text"),
    )
    for value in candidates:
        if isinstance(value, str) and value.strip():
            return value
    raise KeyError("No translated text found in AI4Bharat response")


@router.post("/translate-text", response_model=TranslateTextResponse)
async def translate_text(
    payload: TranslateTextRequest,
    ai4bharat_client: AI4BharatClient = Depends(get_ai4bharat_client),
) -> TranslateTextResponse:
    """Translate or analyse text using the AI4Bharat language models."""

    try:
        result = await ai4bharat_client.translate_text(
            text=payload.text,
            source_language=payload.source_lang,
            target_language=payload.target_lang,
            task=payload.task,
        )
    except AI4BharatAPIError as exc:
        _logger.exception("AI4Bharat translation failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    try:
        translated_text = _extract_translated_text(result)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI4Bharat response missing translated text.",
        ) from exc

    provider_metadata = {
        key: value
        for key, value in result.items()
        if key not in {"translated_text", "translation", "output_text", "text"}
    }
    return TranslateTextResponse(
        translated_text=translated_text,
        source_language=payload.source_lang,
        target_language=payload.target_lang,
        task=payload.task,
        provider_metadata=provider_metadata,
    )


@router.post(
    "/generate-video",
    response_model=GenerateVideoResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def generate_video(
    payload: GenerateVideoRequest,
    ai4bharat_client: AI4BharatClient = Depends(get_ai4bharat_client),
    revid_client: RevidClient = Depends(get_revid_client),
    job_store: JobStore = Depends(get_job_store),
) -> GenerateVideoResponse:
    """Request a Revid.ai video after preparing the roast script with AI4Bharat.

    This endpoint validates that the image contains pets before generating video.
    If no pets are detected, it returns a 400 error asking users to upload pet images/videos.
    """

    # Step 1: Validate pet presence in the image
    pet_detector = get_pet_detector()
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        has_pets, detected_pets, _ = await pet_detector.detect_pets_in_image_url(
            str(payload.image_url),
            client
        )

    if not has_pets:
        _logger.warning(f"No pets detected in image: {payload.image_url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "no_pets_detected",
                "message": "No pets found in the uploaded image. Please upload an image or video containing pets (dogs, cats, birds, etc.) to generate a roast video.",
                "suggestion": "Try uploading a clear photo or video of your pet."
            }
        )

    _logger.info(f"✅ Pets detected: {', '.join(detected_pets)}")

    # Step 2: Proceed with text processing via AI4Bharat
    try:
        llm_result = await ai4bharat_client.translate_text(
            text=payload.text,
            source_language="auto",
            target_language="en",
            task="translation",
        )
        clean_text = _extract_translated_text(llm_result)
    except (AI4BharatAPIError, KeyError) as exc:
        _logger.exception("AI4Bharat preprocessing failed for video generation")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    # Step 3: Create video generation job with Revid
    try:
        revid_response = await revid_client.create_video_job(
            text=clean_text,
            image_url=str(payload.image_url),
            language="en",
        )
    except RevidAPIError as exc:
        _logger.exception("Failed to create Revid job")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    job_id = revid_response["job_id"]
    status_value = _normalise_status(revid_response.get("status", "queued"))
    detail = revid_response.get("detail")

    # Step 4: Store job with detected pets metadata
    record = JobRecord(
        job_id=job_id,
        status=status_value,
        text=clean_text,
        image_url=str(payload.image_url),
        language="en",
        detail=detail,
    )
    await job_store.upsert(record)

    return GenerateVideoResponse(
        job_id=job_id,
        status=status_value,
    )


@router.post("/webhook/video-complete")
async def video_completion_webhook(
    payload: dict,
    job_store: JobStore = Depends(get_job_store),
    settings: Settings = Depends(get_settings_dependency),
) -> dict:
    """Webhook endpoint for Revid.ai to notify when video is complete.

    This endpoint will be called by Revid when video generation completes.
    It updates the job status and notifies the backend via webhook with retry logic.

    Expected payload:
    {
        "job_id": "abc123",
        "status": "completed" | "failed",
        "video_url": "https://...",  // optional, present if completed
        "error": "error message"      // optional, present if failed
    }
    """
    job_id = None
    try:
        # Validate required fields
        job_id = payload.get("job_id")
        status_str = payload.get("status", "completed")
        video_url = payload.get("video_url")
        error = payload.get("error")

        if not job_id:
            _logger.error("❌ Webhook received without job_id")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing job_id in webhook payload"
            )

        _logger.info(f"📥 Webhook received for job {job_id}: status={status_str}")

        # Update job status in store
        stored_record = await job_store.get(job_id)
        if stored_record:
            stored_record.status = _normalise_status(status_str)
            if video_url:
                stored_record.video_url = video_url
                _logger.info(f"📹 Video URL for job {job_id}: {video_url}")
            if error:
                stored_record.detail = error
                _logger.error(f"❌ Job {job_id} failed: {error}")
            await job_store.upsert(stored_record)
            _logger.info(f"✅ Updated job {job_id} in store: {status_str}")
        else:
            _logger.warning(f"⚠️  Job {job_id} not found in store, creating new record")
            # Create new record if not exists
            new_record = JobRecord(
                job_id=job_id,
                status=_normalise_status(status_str),
                text="",
                image_url="",
                language="en",
                video_url=video_url,
                detail=error,
            )
            await job_store.upsert(new_record)

        # Notify backend with retry logic
        backend_webhook_url = settings.backend_webhook_url
        if backend_webhook_url:
            _logger.info(f"🔔 Notifying backend at {backend_webhook_url}")

            webhook_payload = {
                "job_id": job_id,
                "status": status_str,
                "video_url": video_url,
                "error": error,
                "timestamp": None,  # Will be set by backend
            }

            # Retry configuration
            max_retries = 3
            retry_delay = 1.0  # seconds

            for attempt in range(max_retries):
                try:
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(15.0, connect=5.0)
                    ) as client:
                        response = await client.post(
                            backend_webhook_url,
                            json=webhook_payload,
                            headers={
                                "Content-Type": "application/json",
                                "X-Webhook-Source": "pet-roast-ai",
                                "X-Job-ID": job_id,
                            }
                        )
                        response.raise_for_status()
                        _logger.info(
                            f"✅ Backend notified successfully (attempt {attempt + 1}/{max_retries}): "
                            f"status={response.status_code}"
                        )
                        break  # Success, exit retry loop

                except httpx.TimeoutException as e:
                    _logger.warning(
                        f"⏱️  Backend webhook timeout (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        _logger.error(f"❌ Backend notification failed after {max_retries} attempts")

                except httpx.HTTPStatusError as e:
                    _logger.error(
                        f"❌ Backend webhook returned error {e.response.status_code} "
                        f"(attempt {attempt + 1}/{max_retries}): {e.response.text}"
                    )
                    if attempt < max_retries - 1 and e.response.status_code >= 500:
                        # Retry on 5xx errors
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        break  # Don't retry on 4xx errors

                except Exception as e:
                    _logger.error(
                        f"❌ Unexpected error notifying backend (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
        else:
            _logger.debug("ℹ️  No backend webhook URL configured, skipping notification")

        return {
            "status": "success",
            "message": f"Webhook processed for job {job_id}",
            "job_id": job_id,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        _logger.exception(f"❌ Webhook processing failed for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook: {str(e)}"
        )


@router.get("/video-status/{job_id}", response_model=VideoStatusResponse)
async def get_video_status(
    job_id: str,
    revid_client: RevidClient = Depends(get_revid_client),
    job_store: JobStore = Depends(get_job_store),
) -> VideoStatusResponse:
    """Poll Revid.ai for the latest job status."""

    stored_record = await job_store.get(job_id)
    try:
        remote_status = await revid_client.get_job_status(job_id)
        status_value = _normalise_status(remote_status.get("status", "processing"))
        detail = remote_status.get("detail")
        video_url = remote_status.get("video_url")
        if stored_record is None:
            stored_record = JobRecord(
                job_id=job_id,
                status=status_value,
                text="",
                image_url="",
                language="en",
                detail=detail,
                video_url=video_url,
            )
            await job_store.upsert(stored_record)
        else:
            stored_record = await job_store.update(
                job_id,
                status=status_value,
                detail=detail,
                video_url=video_url,
            )
    except RevidAPIError as exc:
        _logger.exception("Revid status retrieval failed")
        if stored_record is None:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
        status_value = stored_record.status
        detail = stored_record.detail

    updated_at = stored_record.updated_at if stored_record else None
    return VideoStatusResponse(
        job_id=job_id,
        status=status_value,
        detail=detail,
        updated_at=updated_at,
    )


@router.get("/video-result/{job_id}", response_model=VideoResultResponse)
async def get_video_result(
    job_id: str,
    revid_client: RevidClient = Depends(get_revid_client),
    job_store: JobStore = Depends(get_job_store),
) -> VideoResultResponse:
    """Retrieve final video URL once Revid.ai completes the job."""

    record = await job_store.get(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job ID not found.")

    if record.status != JobStatus.COMPLETED or not record.video_url:
        try:
            status_payload = await revid_client.get_job_status(job_id)
            status_value = _normalise_status(status_payload.get("status", record.status.value))
            detail = status_payload.get("detail")
            video_url = status_payload.get("video_url")
            record = await job_store.update(
                job_id,
                status=status_value,
                detail=detail,
                video_url=video_url,
            ) or record
        except RevidAPIError as exc:
            _logger.exception("Revid status fetch during result retrieval failed")
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        if record.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Video generation still in progress.",
            )

        if not record.video_url:
            try:
                result_payload = await revid_client.get_job_result(job_id)
            except RevidAPIError as exc:
                _logger.exception("Revid result fetch failed")
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
            if not result_payload or "video_url" not in result_payload:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Video asset not ready yet.",
                )
            record = await job_store.update(
                job_id,
                video_url=result_payload["video_url"],
            ) or record

    return VideoResultResponse(
        job_id=job_id,
        status=record.status,
        video_url=record.video_url,
        detail=record.detail,
    )


@router.get("/test-backend-connection")
async def test_backend_connection(
    settings: Settings = Depends(get_settings_dependency),
) -> dict:
    """Test connectivity to the backend webhook URL.

    This endpoint helps verify that the AI service can reach the backend.
    Returns connection status and response time.
    """
    backend_webhook_url = settings.backend_webhook_url

    if not backend_webhook_url:
        return {
            "status": "not_configured",
            "message": "BACKEND_WEBHOOK_URL environment variable not set",
            "backend_url": None,
        }

    # Test connectivity with a health check payload
    test_payload = {
        "job_id": "test_connection",
        "status": "test",
        "message": "Connection test from AI service"
    }

    import time
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.post(
                backend_webhook_url,
                json=test_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Source": "pet-roast-ai",
                    "X-Test": "true",
                }
            )
            elapsed = time.time() - start_time

            return {
                "status": "success",
                "message": "Backend is reachable",
                "backend_url": backend_webhook_url,
                "response_code": response.status_code,
                "response_time_ms": round(elapsed * 1000, 2),
                "response_body": response.text[:200] if response.text else None,
            }

    except httpx.TimeoutException as e:
        elapsed = time.time() - start_time
        return {
            "status": "timeout",
            "message": f"Backend connection timeout after {elapsed:.2f}s",
            "backend_url": backend_webhook_url,
            "error": str(e),
        }

    except httpx.HTTPStatusError as e:
        elapsed = time.time() - start_time
        return {
            "status": "error",
            "message": f"Backend returned error {e.response.status_code}",
            "backend_url": backend_webhook_url,
            "response_code": e.response.status_code,
            "response_time_ms": round(elapsed * 1000, 2),
            "error": e.response.text[:200] if e.response.text else None,
        }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "status": "failed",
            "message": "Failed to connect to backend",
            "backend_url": backend_webhook_url,
            "response_time_ms": round(elapsed * 1000, 2),
            "error": str(e),
        }


@router.get("/banuba-filters", response_model=BanubaFiltersResponse)
async def list_banuba_filters(
    settings: Settings = Depends(get_settings_dependency),
) -> BanubaFiltersResponse:
    """Expose curated Banuba filter set for the frontend."""

    filters = [BanubaFilter(**filter_config.model_dump()) for filter_config in settings.banuba_filters]
    return BanubaFiltersResponse(filters=filters)


@router.post("/revid-webhook", status_code=status.HTTP_204_NO_CONTENT)
async def handle_revid_webhook(
    request: Request,
    event: RevidWebhookEvent,
    job_store: JobStore = Depends(get_job_store),
    settings: Settings = Depends(get_settings_dependency),
) -> Response:
    """Process webhook callbacks from Revid.ai and update job state."""

    if settings.revid_webhook_secret:
        signature_header = request.headers.get("X-Revid-Signature")
        signature = extract_signature_from_header(signature_header)
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing webhook signature.",
            )
        body = await request.body()
        if not verify_webhook_signature(
            payload=body,
            signature=signature,
            secret=settings.revid_webhook_secret,
        ):
            _logger.warning("Webhook signature verification failed for job %s", event.job_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature.",
            )

    status_value = event.status
    updated = await job_store.update(
        event.job_id,
        status=status_value,
        video_url=str(event.video_url) if event.video_url else None,
        detail=event.detail,
    )
    if updated is None:
        record = JobRecord(
            job_id=event.job_id,
            status=status_value,
            text="",
            image_url="",
            language="en",
            video_url=str(event.video_url) if event.video_url else None,
            detail=event.detail,
        )
        await job_store.upsert(record)

    _logger.info("Processed webhook for job %s with status %s", event.job_id, status_value)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
