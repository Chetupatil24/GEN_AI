# Backend Integration Guide - Pet Roast AI

This document provides a comprehensive guide for integrating the Pet Roast AI system with your backend (Snapchat-like community app).

## 🎯 Overview

Pet Roast AI is a **microservice** that provides:
- ✅ Pet detection in images/videos (validates pet presence before processing)
- 🌐 Multilingual text translation (13+ Indian languages + English)
- 🎬 AI-powered video generation with roast narration
- 🎨 AR filter recommendations (Banuba integration ready)

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Endpoints](#api-endpoints)
3. [Integration Patterns](#integration-patterns)
4. [Webhooks Setup](#webhooks-setup)
5. [Example Backend Client](#example-backend-client)
6. [Deployment Guide](#deployment-guide)
7. [Error Handling](#error-handling)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Your Snapchat-like App                    │
│                        (Backend)                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   User     │  │   Posts    │  │   Media    │           │
│  │ Management │  │  Service   │  │  Storage   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│         │              │                │                   │
│         └──────────────┴────────────────┘                   │
│                        │                                     │
│                        ▼ (HTTP/REST API)                    │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 Pet Roast AI Microservice                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │    Pet     │  │ Translation│  │   Video    │           │
│  │ Detection  │  │  (AI4Bharat)│  │Generation │           │
│  │  (YOLO)    │  │            │  │  (Revid)   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│                                                              │
│  ┌────────────┐  ┌────────────┐                            │
│  │   Redis    │  │  Webhook   │                            │
│  │Job Storage │  │  Handler   │                            │
│  └────────────┘  └────────────┘                            │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼ (Webhook Callback)
┌─────────────────────────────────────────────────────────────┐
│              Your Backend Webhook Endpoint                  │
│         (Receives video completion notifications)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### Base URL
```
Production: https://your-domain.com
Development: http://localhost:8000
```

### 1. Health Check

**Endpoint:** `GET /healthz`

**Purpose:** Check if the service is running

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Translate Text

**Endpoint:** `POST /api/translate-text`

**Purpose:** Translate text between Indian languages

**Request Body:**
```json
{
  "text": "This is a cute dog!",
  "source_lang": "en",
  "target_lang": "hi",
  "task": "translation"
}
```

**Response:**
```json
{
  "translated_text": "यह एक प्यारा कुत्ता है!",
  "source_language": "en",
  "target_language": "hi",
  "task": "translation",
  "provider_metadata": {}
}
```

**Supported Languages:**
- `en` - English
- `hi` - Hindi
- `bn` - Bengali
- `ta` - Tamil
- `te` - Telugu
- `ml` - Malayalam
- `kn` - Kannada
- `gu` - Gujarati
- `mr` - Marathi
- `pa` - Punjabi
- `or` - Odia
- `as` - Assamese
- `ur` - Urdu

---

### 3. Generate Video (with Pet Detection)

**Endpoint:** `POST /api/generate-video`

**Purpose:** Generate AI roast video. **Automatically validates pet presence before processing.**

**Request Body:**
```json
{
  "text": "Roast my lazy dog who sleeps all day!",
  "image_url": "https://your-cdn.com/pets/user123/dog.jpg"
}
```

**Success Response (202 Accepted):**
```json
{
  "job_id": "revid_abc123xyz",
  "status": "queued"
}
```

**Error Response - No Pets Detected (400 Bad Request):**
```json
{
  "detail": {
    "error": "no_pets_detected",
    "message": "No pets found in the uploaded image. Please upload an image or video containing pets (dogs, cats, birds, etc.) to generate a roast video.",
    "suggestion": "Try uploading a clear photo or video of your pet."
  }
}
```

**Pet Detection Logic:**
- ✅ Uses YOLOv5 to detect pets (dogs, cats, birds, horses, etc.)
- ✅ Minimum confidence threshold: 50%
- ✅ Supported pets: dog, cat, bird, horse, sheep, cow, elephant, bear, zebra, giraffe
- ❌ Rejects images without pets immediately (saves API costs!)

---

### 4. Check Video Status

**Endpoint:** `GET /api/video-status/{job_id}`

**Purpose:** Poll for video generation progress

**Response:**
```json
{
  "job_id": "revid_abc123xyz",
  "status": "processing",
  "detail": "Video is being rendered",
  "updated_at": "2025-12-01T10:30:00Z"
}
```

**Status Values:**
- `queued` - Job accepted, waiting to start
- `processing` - Video generation in progress
- `completed` - Video ready
- `failed` - Error occurred

---

### 5. Get Video Result

**Endpoint:** `GET /api/video-result/{job_id}`

**Purpose:** Retrieve final video URL

**Response:**
```json
{
  "job_id": "revid_abc123xyz",
  "status": "completed",
  "video_url": "https://cdn.revid.ai/videos/abc123xyz.mp4",
  "detail": "Video generation successful"
}
```

---

### 6. Get AR Filters

**Endpoint:** `GET /api/banuba-filters`

**Purpose:** List available AR filters for video enhancement

**Response:**
```json
{
  "filters": [
    {
      "id": "desi-fire",
      "name": "Desi Fire",
      "description": "Adds spicy overlays and glow effects for dramatic roasts."
    },
    {
      "id": "pet-maharaja",
      "name": "Pet Maharaja",
      "description": "Turns pets into regal royalty with ornate accessories."
    },
    {
      "id": "bollywood-burn",
      "name": "Bollywood Burn",
      "description": "Provides cinematic lighting and spark particles."
    }
  ]
}
```

---

## 🔄 Integration Patterns

### Pattern 1: Synchronous Upload Flow

**Use Case:** User uploads pet photo immediately

```python
# In your backend when user uploads a pet photo:

import httpx

async def handle_pet_upload(user_id: str, image_url: str, prompt: str):
    """Handle pet photo upload and generate roast video"""

    # 1. Call Pet Roast AI to generate video
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://pet-roast-ai:8000/api/generate-video",
            json={
                "text": prompt,
                "image_url": image_url
            }
        )

        if response.status_code == 400:
            # No pets detected - show error to user
            error = response.json()["detail"]
            return {
                "success": False,
                "message": error["message"],
                "suggestion": error["suggestion"]
            }

        response.raise_for_status()
        data = response.json()
        job_id = data["job_id"]

    # 2. Store job_id in your database
    await db.posts.create({
        "user_id": user_id,
        "job_id": job_id,
        "status": "processing",
        "image_url": image_url,
        "prompt": prompt
    })

    # 3. Return immediately to user
    return {
        "success": True,
        "job_id": job_id,
        "message": "Your roast video is being generated!"
    }
```

---

### Pattern 2: Background Job Processing

**Use Case:** Generate videos in background queue

```python
# Using Celery or similar task queue

@celery.app.task
async def generate_roast_video_task(post_id: str):
    """Background task to generate roast video"""

    # 1. Get post data from database
    post = await db.posts.get(post_id)

    # 2. Call Pet Roast AI
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://pet-roast-ai:8000/api/generate-video",
            json={
                "text": post.prompt,
                "image_url": post.image_url
            }
        )

        if response.status_code == 400:
            # No pets - mark post as invalid
            await db.posts.update(post_id, {
                "status": "failed",
                "error": "no_pets_detected"
            })
            return

        data = response.json()
        job_id = data["job_id"]

    # 3. Update database with job_id
    await db.posts.update(post_id, {
        "job_id": job_id,
        "status": "processing"
    })

    # 4. Poll for completion (or use webhooks)
    while True:
        await asyncio.sleep(5)  # Poll every 5 seconds

        status_response = await client.get(
            f"http://pet-roast-ai:8000/api/video-status/{job_id}"
        )
        status_data = status_response.json()

        if status_data["status"] == "completed":
            # Get final video URL
            result_response = await client.get(
                f"http://pet-roast-ai:8000/api/video-result/{job_id}"
            )
            result = result_response.json()

            # Update database
            await db.posts.update(post_id, {
                "status": "completed",
                "video_url": result["video_url"]
            })
            break

        elif status_data["status"] == "failed":
            await db.posts.update(post_id, {
                "status": "failed"
            })
            break
```

---

## 🪝 Webhooks Setup

### Configure Webhook in .env

```bash
# Pet Roast AI .env file
REVID_WEBHOOK_SECRET=your-secret-key-here
```

### Create Webhook Endpoint in Your Backend

```python
# In your Snapchat-like app backend

from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/webhooks/pet-roast-video-complete")
async def handle_video_completion(request: Request):
    """Receive notifications when videos are ready"""

    # 1. Verify webhook signature
    signature = request.headers.get("X-Revid-Signature")
    body = await request.body()

    expected_signature = hmac.new(
        key=b"your-secret-key-here",
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Parse webhook payload
    data = await request.json()
    job_id = data["job_id"]
    status = data["status"]
    video_url = data.get("video_url")

    # 3. Update your database
    await db.posts.update_by_job_id(job_id, {
        "status": status,
        "video_url": video_url
    })

    # 4. Notify user (push notification, websocket, etc.)
    if status == "completed":
        user = await db.posts.get_user_by_job_id(job_id)
        await send_push_notification(
            user_id=user.id,
            title="Your Roast Video is Ready! 🔥",
            body="Check out your hilarious pet roast!"
        )

    return {"status": "ok"}
```

### Register Webhook URL

Configure in Pet Roast AI or manually via API (if supported by Revid).

---

## 📦 Example Backend Client

See `examples/backend_client.py` for a complete, production-ready client library.

```python
from examples.backend_client import PetRoastClient

# Initialize client
client = PetRoastClient(base_url="http://localhost:8000")

# Generate video with automatic pet detection
result = await client.generate_video_with_retry(
    image_url="https://cdn.example.com/pets/dog.jpg",
    prompt="Roast my lazy dog!",
    max_retries=3
)

if result["success"]:
    print(f"Video URL: {result['video_url']}")
else:
    print(f"Error: {result['error']}")
```

---

## 🚀 Deployment Guide

### Option 1: Docker Compose (Recommended for POC)

```yaml
# docker-compose.yml
version: '3.8'

services:
  pet-roast-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REVID_API_KEY=${REVID_API_KEY}
      - REDIS_URL=redis://redis:6379/0
      - USE_REDIS=true
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  indictrans2:
    build: ./IndicTrans2
    ports:
      - "5000:5000"
    command: python inference_server_simple.py
```

Run:
```bash
docker-compose up -d
```

---

### Option 2: Kubernetes (Production)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pet-roast-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pet-roast-ai
  template:
    metadata:
      labels:
        app: pet-roast-ai
    spec:
      containers:
      - name: api
        image: your-registry/pet-roast-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: REVID_API_KEY
          valueFrom:
            secretKeyRef:
              name: pet-roast-secrets
              key: revid-api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: pet-roast-ai
spec:
  selector:
    app: pet-roast-ai
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## ⚠️ Error Handling

### Common Error Codes

| Status Code | Error | Meaning | Action |
|-------------|-------|---------|--------|
| 400 | `no_pets_detected` | No pets found in image | Ask user to upload pet photo |
| 404 | `Job ID not found` | Invalid job_id | Check job_id or generate new video |
| 409 | `Video still processing` | Not ready yet | Poll again or wait for webhook |
| 502 | `AI4Bharat/Revid error` | External API failure | Retry request |

### Retry Strategy

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def generate_video_with_retry(image_url: str, prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://pet-roast-ai:8000/api/generate-video",
            json={"text": prompt, "image_url": image_url}
        )
        response.raise_for_status()
        return response.json()
```

---

## 📊 Monitoring & Metrics

### Health Checks

```python
# Add to your monitoring system
async def check_pet_roast_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://pet-roast-ai:8000/healthz")
        return response.status_code == 200
```

### Key Metrics to Track

1. **Pet Detection Rate:** % of images with pets detected
2. **Video Generation Success Rate:** % of jobs completed successfully
3. **Average Processing Time:** Time from job creation to completion
4. **API Response Times:** Latency for each endpoint

---

## 🔐 Security Best Practices

1. **API Keys:** Store `REVID_API_KEY` in environment variables or secret managers
2. **Webhook Signatures:** Always verify webhook signatures
3. **Rate Limiting:** Implement rate limiting on your backend to prevent abuse
4. **Image Validation:** Validate image URLs before sending to API
5. **HTTPS:** Use HTTPS in production for all API calls

---

## 📞 Support & Next Steps

### POC Checklist

- [ ] Deploy Pet Roast AI service (Docker/K8s)
- [ ] Test `/api/generate-video` with sample pet images
- [ ] Verify pet detection rejects non-pet images
- [ ] Implement webhook handler in your backend
- [ ] Test end-to-end flow: upload → generate → webhook → display
- [ ] Monitor error rates and performance
- [ ] Add retry logic for failed jobs
- [ ] Integrate with your app's UI

### Need Help?

- Review `examples/backend_client.py` for reference implementation
- Check logs: `docker logs pet-roast-ai`
- Test endpoints with Postman/Insomnia
- Read API schemas in `app/schemas.py`

---

## 🎉 Quick Start Example

```bash
# 1. Start the service
docker-compose up -d

# 2. Test pet detection
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my dog",
    "image_url": "https://example.com/dog.jpg"
  }'

# 3. Check status
curl http://localhost:8000/api/video-status/{job_id}

# 4. Get result
curl http://localhost:8000/api/video-result/{job_id}
```

**That's it! You're ready to integrate Pet Roast AI with your backend! 🚀**
