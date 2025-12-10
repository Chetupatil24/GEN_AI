#!/usr/bin/env python3
"""
Integration Test Script for Pet Roast AI Service and Backend

This script tests the complete integration between:
- AI Service (FastAPI)
- Backend (Node.js/GraphQL)
- External APIs (Revid.ai)

Usage:
    python test_integration.py --ai-service-url https://your-ai-service.railway.app
                               --backend-url https://your-backend.railway.app
                               --test-image https://example.com/dog.jpg
"""

import argparse
import asyncio
import json
import sys
import time
from typing import Dict, Optional

import httpx


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.ENDC}")


class IntegrationTester:
    """Test suite for AI service and backend integration."""

    def __init__(self, ai_service_url: str, backend_url: Optional[str], test_image: str):
        self.ai_service_url = ai_service_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/') if backend_url else None
        self.test_image = test_image
        self.test_results = []

    async def test_ai_service_health(self) -> bool:
        """Test 1: AI service health check."""
        print_header("Test 1: AI Service Health Check")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.ai_service_url}/healthz")

                if response.status_code == 200:
                    data = response.json()
                    print_success(f"AI service is healthy: {json.dumps(data)}")
                    return True
                else:
                    print_error(f"Health check failed: {response.status_code}")
                    return False

        except Exception as e:
            print_error(f"Failed to connect to AI service: {e}")
            return False

    async def test_backend_connectivity(self) -> bool:
        """Test 2: Backend connectivity test."""
        print_header("Test 2: Backend Connectivity")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.ai_service_url}/api/test-backend-connection"
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')

                    if status == 'not_configured':
                        print_warning("Backend webhook URL not configured")
                        print_info("Set BACKEND_WEBHOOK_URL environment variable")
                        return False
                    elif status == 'success':
                        print_success(f"Backend is reachable at {data.get('backend_url')}")
                        print_info(f"Response time: {data.get('response_time_ms')}ms")
                        return True
                    else:
                        print_error(f"Backend connection failed: {data.get('message')}")
                        print_info(f"Error: {data.get('error', 'Unknown')}")
                        return False
                else:
                    print_error(f"Test endpoint failed: {response.status_code}")
                    return False

        except Exception as e:
            print_error(f"Failed to test backend connectivity: {e}")
            return False

    async def test_generate_video(self) -> Optional[str]:
        """Test 3: Generate video with pet detection."""
        print_header("Test 3: Generate Video (with Pet Detection)")

        payload = {
            "text": "Roast my adorable lazy pet!",
            "image_url": self.test_image
        }

        print_info(f"Sending request to generate video...")
        print_info(f"Image URL: {self.test_image}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ai_service_url}/api/generate-video",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 202:
                    data = response.json()
                    job_id = data.get('job_id')
                    print_success(f"Video generation started!")
                    print_info(f"Job ID: {job_id}")
                    print_info(f"Status: {data.get('status')}")
                    return job_id

                elif response.status_code == 400:
                    error_data = response.json()
                    detail = error_data.get('detail', {})

                    if isinstance(detail, dict) and detail.get('error') == 'no_pets_detected':
                        print_warning("No pets detected in the image")
                        print_info(f"Message: {detail.get('message')}")
                        print_info(f"Suggestion: {detail.get('suggestion')}")
                    else:
                        print_error(f"Bad request: {detail}")
                    return None

                else:
                    print_error(f"Unexpected response: {response.status_code}")
                    print_info(f"Body: {response.text[:200]}")
                    return None

        except Exception as e:
            print_error(f"Failed to generate video: {e}")
            return None

    async def test_video_status(self, job_id: str) -> Dict:
        """Test 4: Check video status."""
        print_header(f"Test 4: Check Video Status (Job: {job_id})")

        print_info("Polling for video status...")
        max_polls = 10
        poll_interval = 5  # seconds

        for i in range(max_polls):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{self.ai_service_url}/api/video-status/{job_id}"
                    )

                    if response.status_code == 200:
                        data = response.json()
                        status = data.get('status')
                        video_url = data.get('video_url')

                        print_info(f"Poll {i+1}/{max_polls}: Status = {status}")

                        if status == 'completed' and video_url:
                            print_success("Video generation completed!")
                            print_info(f"Video URL: {video_url}")
                            return data

                        elif status == 'failed':
                            print_error(f"Video generation failed: {data.get('detail')}")
                            return data

                        elif i < max_polls - 1:
                            print_info(f"Waiting {poll_interval}s before next poll...")
                            await asyncio.sleep(poll_interval)
                    else:
                        print_error(f"Status check failed: {response.status_code}")
                        return {}

            except Exception as e:
                print_error(f"Failed to check status: {e}")
                return {}

        print_warning("Max polls reached, video may still be processing")
        return {}

    async def test_manual_webhook(self, job_id: str) -> bool:
        """Test 5: Manually trigger webhook to backend."""
        print_header("Test 5: Manual Webhook Test")

        if not self.backend_url:
            print_warning("Backend URL not provided, skipping webhook test")
            return False

        webhook_url = f"{self.backend_url}/webhooks/pet-roast-complete"
        payload = {
            "job_id": job_id,
            "status": "completed",
            "video_url": "https://example.com/test-video.mp4",
            "timestamp": time.time()
        }

        print_info(f"Sending webhook to: {webhook_url}")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Source": "pet-roast-ai",
                        "X-Test": "true"
                    }
                )

                if response.status_code in [200, 201, 204]:
                    print_success(f"Webhook accepted by backend: {response.status_code}")
                    if response.text:
                        print_info(f"Response: {response.text[:200]}")
                    return True
                else:
                    print_error(f"Webhook failed: {response.status_code}")
                    print_info(f"Response: {response.text[:200]}")
                    return False

        except Exception as e:
            print_error(f"Failed to send webhook: {e}")
            return False

    async def run_all_tests(self):
        """Run all integration tests."""
        print(f"\n{Colors.BOLD}🧪 Pet Roast Integration Test Suite{Colors.ENDC}")
        print(f"{Colors.BOLD}AI Service: {self.ai_service_url}{Colors.ENDC}")
        if self.backend_url:
            print(f"{Colors.BOLD}Backend: {self.backend_url}{Colors.ENDC}")
        print(f"{Colors.BOLD}Test Image: {self.test_image}{Colors.ENDC}")

        # Test 1: Health check
        health_ok = await self.test_ai_service_health()
        self.test_results.append(('Health Check', health_ok))

        if not health_ok:
            print_error("AI service is not healthy, aborting tests")
            return

        # Test 2: Backend connectivity
        backend_ok = await self.test_backend_connectivity()
        self.test_results.append(('Backend Connectivity', backend_ok))

        # Test 3: Generate video
        job_id = await self.test_generate_video()
        video_generated = job_id is not None
        self.test_results.append(('Generate Video', video_generated))

        if not job_id:
            print_warning("Skipping remaining tests (no job ID)")
            self.print_summary()
            return

        # Test 4: Video status
        status_data = await self.test_video_status(job_id)
        status_ok = bool(status_data)
        self.test_results.append(('Video Status', status_ok))

        # Test 5: Manual webhook (if backend URL provided)
        if self.backend_url:
            webhook_ok = await self.test_manual_webhook(job_id)
            self.test_results.append(('Manual Webhook', webhook_ok))

        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print_header("Test Summary")

        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)

        for test_name, result in self.test_results:
            if result:
                print_success(f"{test_name}: PASSED")
            else:
                print_error(f"{test_name}: FAILED")

        print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")

        if passed == total:
            print_success("All tests passed! Integration is working correctly. 🎉")
        elif passed > 0:
            print_warning(f"{total - passed} test(s) failed. Check the logs above.")
        else:
            print_error("All tests failed. Check your configuration.")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test Pet Roast AI Service and Backend Integration'
    )
    parser.add_argument(
        '--ai-service-url',
        required=True,
        help='AI service URL (e.g., https://your-ai-service.railway.app)'
    )
    parser.add_argument(
        '--backend-url',
        help='Backend URL (e.g., https://your-backend.railway.app)'
    )
    parser.add_argument(
        '--test-image',
        default='https://images.unsplash.com/photo-1543466835-00a7907e9de1',
        help='Test pet image URL (default: sample dog image)'
    )

    args = parser.parse_args()

    tester = IntegrationTester(
        ai_service_url=args.ai_service_url,
        backend_url=args.backend_url,
        test_image=args.test_image
    )

    await tester.run_all_tests()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        sys.exit(1)
