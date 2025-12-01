"""
Production-ready client library for integrating Pet Roast AI with your backend.

This client provides:
- Automatic retry logic
- Pet detection validation
- Webhook signature verification
- Connection pooling
- Comprehensive error handling

Usage:
    from examples.backend_client import PetRoastClient

    client = PetRoastClient(base_url="http://localhost:8000")

    # Generate video with automatic retry
    result = await client.generate_video_with_retry(
        image_url="https://cdn.example.com/pets/dog.jpg",
        prompt="Roast my lazy dog!"
    )

    if result["success"]:
        print(f"Video URL: {result['video_url']}")
"""

import asyncio
import hmac
import hashlib
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


_logger = logging.getLogger(__name__)


class VideoStatus(str, Enum):
    """Video generation job status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PetRoastError(Exception):
    """Base exception for Pet Roast AI client"""
    pass


class NoPetsDetectedError(PetRoastError):
    """Raised when no pets are found in the uploaded image"""
    pass


class VideoGenerationError(PetRoastError):
    """Raised when video generation fails"""
    pass


class PetRoastClient:
    """
    Production-ready client for Pet Roast AI microservice.

    Features:
    - Automatic retries with exponential backoff
    - Connection pooling
    - Pet detection validation
    - Comprehensive error handling
    - Polling with timeout
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        max_retries: int = 3,
        webhook_secret: Optional[str] = None,
    ):
        """
        Initialize Pet Roast AI client.

        Args:
            base_url: Base URL of Pet Roast AI service
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            webhook_secret: Secret key for webhook signature verification
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout)
        self.max_retries = max_retries
        self.webhook_secret = webhook_secret

        # Create persistent HTTP client with connection pooling
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
        return self._client

    async def health_check(self) -> bool:
        """
        Check if Pet Roast AI service is healthy.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/healthz")
            return response.status_code == 200
        except Exception as e:
            _logger.error(f"Health check failed: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def translate_text(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi",
        task: str = "translation",
    ) -> Dict[str, Any]:
        """
        Translate text between languages.

        Args:
            text: Text to translate
            source_lang: Source language code (e.g., 'en', 'hi')
            target_lang: Target language code
            task: Task type ('translation', 'transliteration', etc.)

        Returns:
            Translation result with metadata

        Raises:
            PetRoastError: If translation fails
        """
        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/api/translate-text",
                json={
                    "text": text,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "task": task,
                }
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            _logger.error(f"Translation failed: {e}")
            raise PetRoastError(f"Translation failed: {e.response.text}")

    async def generate_video(
        self,
        image_url: str,
        prompt: str,
    ) -> Dict[str, Any]:
        """
        Generate roast video from pet image.

        This method automatically validates pet presence before generation.

        Args:
            image_url: URL of pet image/video
            prompt: Roast prompt/text

        Returns:
            {
                "job_id": "revid_abc123",
                "status": "queued"
            }

        Raises:
            NoPetsDetectedError: If no pets are found in the image
            PetRoastError: If video generation fails
        """
        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/api/generate-video",
                json={
                    "text": prompt,
                    "image_url": image_url,
                }
            )

            # Handle no pets detected error
            if response.status_code == 400:
                error_data = response.json()
                if isinstance(error_data.get("detail"), dict):
                    detail = error_data["detail"]
                    if detail.get("error") == "no_pets_detected":
                        raise NoPetsDetectedError(detail["message"])
                raise PetRoastError(f"Bad request: {error_data}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            _logger.error(f"Video generation failed: {e}")
            raise PetRoastError(f"Video generation failed: {e.response.text}")

    async def get_video_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get video generation status.

        Args:
            job_id: Job ID returned from generate_video()

        Returns:
            {
                "job_id": "revid_abc123",
                "status": "processing",
                "detail": "Video is being rendered",
                "updated_at": "2025-12-01T10:30:00Z"
            }
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/api/video-status/{job_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            _logger.error(f"Failed to get video status: {e}")
            raise PetRoastError(f"Failed to get video status: {e.response.text}")

    async def get_video_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get final video URL (only works when status is 'completed').

        Args:
            job_id: Job ID returned from generate_video()

        Returns:
            {
                "job_id": "revid_abc123",
                "status": "completed",
                "video_url": "https://cdn.revid.ai/videos/abc123.mp4",
                "detail": "Video generation successful"
            }

        Raises:
            VideoGenerationError: If video is not ready yet
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/api/video-result/{job_id}")

            if response.status_code == 409:
                raise VideoGenerationError("Video is still processing")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            _logger.error(f"Failed to get video result: {e}")
            raise PetRoastError(f"Failed to get video result: {e.response.text}")

    async def get_ar_filters(self) -> List[Dict[str, str]]:
        """
        Get available AR filters.

        Returns:
            List of filter metadata:
            [
                {
                    "id": "desi-fire",
                    "name": "Desi Fire",
                    "description": "Adds spicy overlays..."
                },
                ...
            ]
        """
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/api/banuba-filters")
            response.raise_for_status()
            data = response.json()
            return data["filters"]
        except httpx.HTTPStatusError as e:
            _logger.error(f"Failed to get AR filters: {e}")
            raise PetRoastError(f"Failed to get AR filters: {e.response.text}")

    async def poll_until_complete(
        self,
        job_id: str,
        poll_interval: float = 5.0,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """
        Poll video status until completion or timeout.

        Args:
            job_id: Job ID to poll
            poll_interval: Seconds between polls
            timeout: Maximum time to wait (seconds)

        Returns:
            Final video result with video_url

        Raises:
            TimeoutError: If video doesn't complete within timeout
            VideoGenerationError: If video generation fails
        """
        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Video generation timed out after {timeout}s")

            status_data = await self.get_video_status(job_id)
            status = VideoStatus(status_data["status"])

            _logger.info(f"Job {job_id} status: {status.value}")

            if status == VideoStatus.COMPLETED:
                # Get final result with video URL
                return await self.get_video_result(job_id)

            elif status == VideoStatus.FAILED:
                raise VideoGenerationError(
                    f"Video generation failed: {status_data.get('detail', 'Unknown error')}"
                )

            # Still processing, wait and poll again
            await asyncio.sleep(poll_interval)

    async def generate_video_with_retry(
        self,
        image_url: str,
        prompt: str,
        poll_interval: float = 5.0,
        timeout: float = 300.0,
    ) -> Dict[str, Any]:
        """
        High-level method: Generate video and wait for completion.

        This is the recommended method for most use cases. It:
        1. Validates pet presence
        2. Starts video generation
        3. Polls until completion
        4. Returns final video URL

        Args:
            image_url: URL of pet image
            prompt: Roast prompt
            poll_interval: Seconds between status polls
            timeout: Maximum wait time

        Returns:
            {
                "success": True,
                "job_id": "revid_abc123",
                "video_url": "https://cdn.revid.ai/videos/abc123.mp4",
                "status": "completed"
            }

            Or on error:
            {
                "success": False,
                "error": "no_pets_detected",
                "message": "No pets found in image..."
            }
        """
        try:
            # Step 1: Generate video (validates pets automatically)
            generation_result = await self.generate_video(image_url, prompt)
            job_id = generation_result["job_id"]

            _logger.info(f"Video generation started: {job_id}")

            # Step 2: Poll until complete
            final_result = await self.poll_until_complete(
                job_id=job_id,
                poll_interval=poll_interval,
                timeout=timeout,
            )

            return {
                "success": True,
                "job_id": job_id,
                "video_url": final_result["video_url"],
                "status": final_result["status"],
            }

        except NoPetsDetectedError as e:
            _logger.warning(f"No pets detected: {e}")
            return {
                "success": False,
                "error": "no_pets_detected",
                "message": str(e),
            }

        except (VideoGenerationError, TimeoutError) as e:
            _logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error": "generation_failed",
                "message": str(e),
            }

        except PetRoastError as e:
            _logger.error(f"Pet Roast AI error: {e}")
            return {
                "success": False,
                "error": "api_error",
                "message": str(e),
            }

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Pet Roast AI.

        Args:
            payload: Raw webhook request body (bytes)
            signature: Signature from X-Revid-Signature header

        Returns:
            True if signature is valid, False otherwise
        """
        if not self.webhook_secret:
            _logger.warning("No webhook secret configured, skipping verification")
            return True

        expected_signature = hmac.new(
            key=self.webhook_secret.encode(),
            msg=payload,
            digestmod=hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)


# =============================================================================
# Example Usage for Snapchat-like Backend Integration
# =============================================================================

async def example_integration():
    """
    Example: How to integrate Pet Roast AI with your Snapchat-like backend.
    """

    # Initialize client (use environment variable in production)
    async with PetRoastClient(base_url="http://localhost:8000") as client:

        # 1. Health check
        is_healthy = await client.health_check()
        print(f"Service healthy: {is_healthy}")

        # 2. Generate video with automatic pet detection
        result = await client.generate_video_with_retry(
            image_url="https://images.dog.ceo/breeds/husky/n02110185_10047.jpg",
            prompt="Roast my dramatic husky who howls at everything!",
        )

        if result["success"]:
            print(f"✅ Video generated successfully!")
            print(f"   Job ID: {result['job_id']}")
            print(f"   Video URL: {result['video_url']}")
        else:
            print(f"❌ Failed: {result['error']}")
            print(f"   Message: {result['message']}")


# Example webhook handler for your backend
async def webhook_handler_example(request_body: bytes, signature: str):
    """
    Example webhook handler for receiving video completion notifications.

    Add this to your backend's webhook endpoint.
    """
    client = PetRoastClient(webhook_secret="your-secret-key")

    # Verify signature
    if not client.verify_webhook_signature(request_body, signature):
        raise ValueError("Invalid webhook signature")

    # Parse webhook data
    import json
    data = json.loads(request_body)

    job_id = data["job_id"]
    status = data["status"]
    video_url = data.get("video_url")

    print(f"Webhook received: {job_id} -> {status}")

    # Update your database
    # await db.posts.update_by_job_id(job_id, {"status": status, "video_url": video_url})

    # Send push notification to user
    if status == "completed":
        # await send_push_notification(user_id, "Your roast video is ready!")
        pass


if __name__ == "__main__":
    # Run example
    asyncio.run(example_integration())
