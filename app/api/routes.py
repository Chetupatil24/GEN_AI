"""API route definitions for the pet roasting backend."""

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
    request: Request = None,
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
