#!/usr/bin/env python3
"""
Quick test script to verify AI service and backend connection.
Run this after deploying to Railway to ensure everything works.
"""

import requests
import sys
import time
from typing import Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_ai_service_health(ai_url: str) -> bool:
    """Test if AI service is running"""
    print(f"\n{Colors.BOLD}Testing AI Service Health...{Colors.END}")
    try:
        response = requests.get(f"{ai_url}/healthz", timeout=10)
        if response.status_code == 200 and response.json().get("status") == "ok":
            print_success(f"AI Service is running at {ai_url}")
            return True
        else:
            print_error(f"AI Service returned unexpected response: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to AI service at {ai_url}")
        print_info("Make sure your Railway deployment is complete")
        return False
    except Exception as e:
        print_error(f"Error testing AI service: {e}")
        return False

def test_backend_connection(ai_url: str) -> bool:
    """Test if AI service can reach backend"""
    print(f"\n{Colors.BOLD}Testing Backend Connection...{Colors.END}")
    try:
        response = requests.get(f"{ai_url}/api/test-backend-connection", timeout=10)
        data = response.json()

        status = data.get("status")
        backend_url = data.get("backend_url")

        if status == "success":
            print_success(f"Backend is reachable at {backend_url}")
            print_info(f"Response time: {data.get('response_time_ms', 0):.2f}ms")
            return True
        elif status == "not_configured":
            print_warning("Backend webhook URL not configured")
            print_info("Set BACKEND_WEBHOOK_URL environment variable in Railway")
            return False
        else:
            print_error(f"Backend connection failed: {data.get('message')}")
            if backend_url:
                print_info(f"Backend URL: {backend_url}")
            return False
    except Exception as e:
        print_error(f"Error testing backend connection: {e}")
        return False

def test_video_generation(ai_url: str) -> Optional[str]:
    """Test video generation with a sample image"""
    print(f"\n{Colors.BOLD}Testing Video Generation...{Colors.END}")

    # Use a public dog image from Unsplash
    test_image = "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
    test_text = "This is a test roast for deployment verification"

    try:
        print_info("Submitting video generation request...")
        response = requests.post(
            f"{ai_url}/api/generate-video",
            json={
                "text": test_text,
                "image_url": test_image
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print_success(f"Video generation started: Job ID = {job_id}")
            return job_id
        elif response.status_code == 400:
            error = response.json().get("detail", "Unknown error")
            print_error(f"Video generation failed: {error}")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Error testing video generation: {e}")
        return None

def test_video_status(ai_url: str, job_id: str) -> bool:
    """Test video status endpoint"""
    print(f"\n{Colors.BOLD}Testing Video Status Check...{Colors.END}")

    try:
        response = requests.get(f"{ai_url}/api/video-status/{job_id}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print_success(f"Status check working: Job status = {status}")

            if status == "completed":
                video_url = data.get("video_url")
                print_success(f"Video URL: {video_url}")

            return True
        elif response.status_code == 404:
            print_error("Job not found (this might be expected if job expired)")
            return False
        else:
            print_error(f"Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error checking video status: {e}")
        return False

def test_api_docs(ai_url: str) -> bool:
    """Test if API documentation is accessible"""
    print(f"\n{Colors.BOLD}Testing API Documentation...{Colors.END}")
    try:
        response = requests.get(f"{ai_url}/docs", timeout=10)
        if response.status_code == 200:
            print_success(f"API docs available at {ai_url}/docs")
            return True
        else:
            print_warning("API docs not accessible")
            return False
    except Exception as e:
        print_error(f"Error accessing API docs: {e}")
        return False

def main():
    print(f"""
{Colors.BOLD}{Colors.BLUE}
╔═══════════════════════════════════════════════════════════╗
║     Pet Roast AI - Deployment Verification Test          ║
╚═══════════════════════════════════════════════════════════╝
{Colors.END}
""")

    # Get AI service URL
    if len(sys.argv) > 1:
        ai_url = sys.argv[1].rstrip('/')
    else:
        print(f"{Colors.YELLOW}Usage: python test_deployment.py <AI_SERVICE_URL>{Colors.END}")
        print(f"{Colors.YELLOW}Example: python test_deployment.py https://your-ai-service.up.railway.app{Colors.END}\n")
        ai_url = input(f"{Colors.BLUE}Enter your AI Service URL: {Colors.END}").strip().rstrip('/')

        if not ai_url:
            print_error("No URL provided. Exiting.")
            sys.exit(1)

    print_info(f"Testing AI Service at: {ai_url}\n")
    print("=" * 60)

    # Run tests
    results = []

    # Test 1: Health check
    results.append(("Health Check", test_ai_service_health(ai_url)))

    if not results[0][1]:
        print_error("\nAI Service is not reachable. Please check your Railway deployment.")
        sys.exit(1)

    # Test 2: Backend connection
    results.append(("Backend Connection", test_backend_connection(ai_url)))

    # Test 3: API documentation
    results.append(("API Documentation", test_api_docs(ai_url)))

    # Test 4: Video generation
    job_id = test_video_generation(ai_url)
    results.append(("Video Generation", job_id is not None))

    # Test 5: Video status (if we got a job_id)
    if job_id:
        time.sleep(2)  # Wait a bit before checking status
        results.append(("Video Status Check", test_video_status(ai_url, job_id)))

    # Print summary
    print("\n" + "=" * 60)
    print(f"\n{Colors.BOLD}Test Summary:{Colors.END}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.END}" if result else f"{Colors.RED}❌ FAILED{Colors.END}"
        print(f"  {test_name:.<40} {status}")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Your deployment is ready!{Colors.END}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.END}")
        print(f"  1. Update your backend with AI service URL: {ai_url}")
        print(f"  2. Implement webhook endpoint in your backend")
        print(f"  3. Test the complete flow from your app")
        print(f"  4. View API docs: {ai_url}/docs")
    elif results[0][1]:  # Health check passed but others failed
        print(f"\n{Colors.YELLOW}⚠️  Service is running but some features need configuration{Colors.END}")
        print(f"\n{Colors.BLUE}Required actions:{Colors.END}")
        if not results[1][1]:  # Backend connection failed
            print(f"  • Set BACKEND_WEBHOOK_URL in Railway environment variables")
        print(f"  • Check Railway logs for detailed error messages")
        print(f"  • Verify all environment variables are set correctly")
    else:
        print(f"\n{Colors.RED}❌ Deployment verification failed{Colors.END}")
        print(f"\n{Colors.BLUE}Troubleshooting:{Colors.END}")
        print(f"  • Check if Railway deployment completed successfully")
        print(f"  • View logs: railway logs")
        print(f"  • Verify Dockerfile built correctly")
        print(f"  • Check environment variables in Railway dashboard")

    print()

if __name__ == "__main__":
    main()
