# 📡 API Reference - Pet Roast AI Service

Complete API documentation for backend integration.

---

## Base URL

```
Production: https://your-ai-service.railway.app
Local: http://localhost:8000
```

---

## Authentication

Currently no authentication required. For production, consider adding API keys.

---

## Endpoints

### 1. Health Check

Check if the service is running.

**Endpoint:** `GET /healthz`

**Response 200:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl https://your-ai-service.railway.app/healthz
```

---

### 2. Test Backend Connection

Test connectivity to the configured backend webhook URL.

**Endpoint:** `GET /api/test-backend-connection`

**Response 200 (Success):**
```json
{
  "status": "success",
  "message": "Backend is reachable",
  "backend_url": "https://your-backend.railway.app/webhooks/pet-roast-complete",
  "response_code": 200,
  "response_time_ms": 145.23,
  "response_body": "{\"status\":\"success\"}"
}
```

**Response 200 (Not Configured):**
```json
{
  "status": "not_configured",
  "message": "BACKEND_WEBHOOK_URL environment variable not set",
  "backend_url": null
}
```

**Response 200 (Failed):**
```json
{
  "status": "failed",
  "message": "Failed to connect to backend",
  "backend_url": "https://your-backend.railway.app/webhooks/pet-roast-complete",
  "response_time_ms": 10005.67,
  "error": "Connection timeout"
}
```

**Example:**
```bash
curl https://your-ai-service.railway.app/api/test-backend-connection
```

---

### 3. Generate Video

Generate a roast video with pet detection validation.

**Endpoint:** `POST /api/generate-video`

**Request Body:**
```json
{
  "text": "Roast my lazy dog!",
  "image_url": "https://example.com/dog.jpg"
}
```

**Request Parameters:**
- `text` (string, required): Roast text in any language (will be translated to English)
- `image_url` (string, required): Publicly accessible URL to pet image

**Response 202 (Accepted):**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "queued"
}
```

**Response 400 (No Pets Detected):**
```json
{
  "detail": {
    "error": "no_pets_detected",
    "message": "No pets found in the uploaded image. Please upload an image or video containing pets (dogs, cats, birds, etc.) to generate a roast video.",
    "suggestion": "Try uploading a clear photo or video of your pet."
  }
}
```

**Response 502 (Service Error):**
```json
{
  "detail": "AI4Bharat translation failed: Connection timeout"
}
```

**Supported Pets:**
- dog, cat, bird, horse, sheep, cow, elephant, bear, zebra, giraffe

**Example:**
```bash
curl -X POST https://your-ai-service.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my lazy dog!",
    "image_url": "https://example.com/dog.jpg"
  }'
```

**Backend Implementation:**
```typescript
interface GenerateVideoRequest {
  text: string;
  image_url: string;
}

interface GenerateVideoResponse {
  job_id: string;
  status: "queued" | "processing";
}

async function generatePetRoast(text: string, imageUrl: string): Promise<string> {
  const response = await fetch(`${AI_SERVICE_URL}/api/generate-video`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, image_url: imageUrl })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.message || 'Failed to generate video');
  }

  const { job_id } = await response.json();
  return job_id;
}
```

---

### 4. Check Video Status

Poll for video generation status.

**Endpoint:** `GET /api/video-status/{job_id}`

**Path Parameters:**
- `job_id` (string, required): Job ID returned from generate-video

**Response 200 (Processing):**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "processing",
  "detail": null,
  "updated_at": "2025-12-07T10:00:00Z"
}
```

**Response 200 (Completed):**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "completed",
  "detail": null,
  "updated_at": "2025-12-07T10:05:00Z",
  "video_url": "https://revid.ai/videos/abc123.mp4"
}
```

**Response 200 (Failed):**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "failed",
  "detail": "Revid.ai processing failed: Invalid video parameters",
  "updated_at": "2025-12-07T10:03:00Z"
}
```

**Status Values:**
- `queued`: Job is queued
- `processing`: Video is being generated
- `completed`: Video is ready (includes video_url)
- `failed`: Generation failed (includes error detail)

**Example:**
```bash
curl https://your-ai-service.railway.app/api/video-status/rev_abc123xyz
```

**Backend Implementation:**
```typescript
interface VideoStatusResponse {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  detail?: string;
  updated_at?: string;
  video_url?: string;
}

async function pollVideoStatus(jobId: string): Promise<VideoStatusResponse> {
  const response = await fetch(`${AI_SERVICE_URL}/api/video-status/${jobId}`);
  return await response.json();
}

// Poll until completed or failed
async function waitForVideo(jobId: string): Promise<string> {
  const maxAttempts = 60; // 5 minutes with 5s intervals

  for (let i = 0; i < maxAttempts; i++) {
    const status = await pollVideoStatus(jobId);

    if (status.status === 'completed' && status.video_url) {
      return status.video_url;
    }

    if (status.status === 'failed') {
      throw new Error(status.detail || 'Video generation failed');
    }

    await new Promise(resolve => setTimeout(resolve, 5000));
  }

  throw new Error('Video generation timeout');
}
```

---

### 5. Video Completion Webhook (AI → Backend)

**This endpoint should be implemented in YOUR backend, not called by you.**

The AI service will call this endpoint when video generation completes.

**Your Backend Endpoint:** `POST /webhooks/pet-roast-complete`

**Request from AI Service:**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "completed",
  "video_url": "https://revid.ai/videos/abc123.mp4",
  "timestamp": null
}
```

**Request Headers from AI Service:**
```
Content-Type: application/json
X-Webhook-Source: pet-roast-ai
X-Job-ID: rev_abc123xyz
```

**Expected Response from Your Backend:**
```json
{
  "status": "success",
  "message": "Job rev_abc123xyz updated successfully"
}
```

**Webhook Retry Logic:**
- AI service retries up to 3 times on timeout or 5xx errors
- Exponential backoff: 1s, 2s, 3s
- 15 second timeout per attempt
- 4xx errors are not retried

**Backend Implementation Example:**
```typescript
// Express.js example
app.post('/webhooks/pet-roast-complete', async (req, res) => {
  try {
    const { job_id, status, video_url, error } = req.body;

    console.log('📥 Webhook received:', { job_id, status });

    // Find job in database
    const job = await db.roastJobs.findOne({ jobId: job_id });
    if (!job) {
      console.warn('Job not found:', job_id);
      return res.json({ status: 'success', message: 'Job not found' });
    }

    // Update job
    job.status = status;
    job.videoUrl = video_url;
    job.error = error;
    job.updatedAt = new Date();
    await job.save();

    // Send push notification to user
    if (status === 'completed' && video_url) {
      await sendPushNotification(job.userId, {
        title: '🎬 Your Pet Roast is Ready!',
        body: 'Your video is ready to watch!',
        data: { videoUrl: video_url }
      });
    }

    res.json({ status: 'success', message: `Job ${job_id} updated` });

  } catch (error) {
    console.error('Webhook error:', error);
    // Return 200 anyway to prevent retries
    res.json({ status: 'error', message: error.message });
  }
});
```

**NestJS Example:**
```typescript
@Controller('webhooks')
export class WebhookController {
  @Post('pet-roast-complete')
  @HttpCode(200)
  async handleVideoComplete(@Body() payload: VideoCompletePayload) {
    const { job_id, status, video_url, error } = payload;

    const job = await this.roastJobRepository.findByJobId(job_id);
    if (!job) {
      return { status: 'success', message: 'Job not found' };
    }

    job.status = status;
    job.videoUrl = video_url;
    job.error = error;
    await this.roastJobRepository.save(job);

    if (status === 'completed' && video_url) {
      await this.notificationService.sendVideoReady(job.userId, video_url);
    }

    return { status: 'success', message: `Job ${job_id} updated` };
  }
}
```

---

### 6. Get Video Result (Deprecated - Use video-status instead)

Retrieve final video URL once generation completes.

**Endpoint:** `GET /api/video-result/{job_id}`

**Note:** This endpoint is similar to `video-status` but may make additional API calls to Revid.ai. Use `video-status` for polling instead.

---

### 7. Translate Text (Standalone Translation)

Translate text using AI4Bharat without generating video.

**Endpoint:** `POST /api/translate-text`

**Request Body:**
```json
{
  "text": "मेरे कुत्ते को भुनाओ",
  "source_lang": "hi",
  "target_lang": "en",
  "task": "translation"
}
```

**Response 200:**
```json
{
  "translated_text": "Roast my dog",
  "source_language": "hi",
  "target_language": "en",
  "task": "translation",
  "provider_metadata": {}
}
```

**Example:**
```bash
curl -X POST https://your-ai-service.railway.app/api/translate-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "मेरे कुत्ते को भुनाओ",
    "source_lang": "hi",
    "target_lang": "en",
    "task": "translation"
  }'
```

---

## Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | Success | Request completed successfully |
| 202 | Accepted | Video generation started (async) |
| 400 | Bad Request | No pets detected, invalid parameters |
| 404 | Not Found | Job ID not found |
| 409 | Conflict | Video still processing (not ready) |
| 502 | Bad Gateway | External service (Revid, AI4Bharat) failed |
| 500 | Server Error | Internal error |

---

## Rate Limits

Currently no rate limiting. For production, consider implementing rate limits based on:
- IP address
- API key
- User ID

---

## Environment Variables

Configure these in Railway or `.env`:

```env
# Required
REVID_API_KEY=your_revid_api_key

# Backend Integration (Required for webhooks)
BACKEND_WEBHOOK_URL=https://your-backend.railway.app/webhooks/pet-roast-complete
CORS_ORIGINS=["https://your-backend.railway.app"]

# Redis (Required for job persistence)
REDIS_URL=redis://default:password@redis.railway.internal:6379
USE_REDIS=true

# Optional
AI4BHARAT_BASE_URL=http://localhost:5000
AI4BHARAT_API_KEY=
REVID_WEBHOOK_SECRET=
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
```

---

## Complete Integration Flow

```
┌──────────────┐
│ Mobile App   │
└──────┬───────┘
       │ GraphQL: generateRoast(petId, text, imageUrl)
       ▼
┌─────────────────────────────────────────────┐
│ Your Backend (Node.js)                      │
│                                             │
│ 1. Validate user & pet                      │
│ 2. Upload image to storage                  │
│ 3. Call AI service ──────────────────┐     │
│ 4. Store job_id in database          │     │
│ 5. Return job_id to app              │     │
└──────────────▲──────────────────────────────┘
               │                              │
               │ Webhook when                 │ REST API
               │ video ready                  │
               │                              ▼
        ┌──────┴───────────────────────────────────────┐
        │ AI Service (FastAPI)                         │
        │                                              │
        │ 1. Detect pets (YOLOv5)     ✓               │
        │ 2. Translate text (AI4Bharat) ✓             │
        │ 3. Generate video (Revid.ai)  ✓             │
        │ 4. Store in Redis             ✓             │
        │ 5. Webhook backend when done  ✓             │
        └──────────────────────────────────────────────┘
                                       │
                                       ▼
                               Revid.ai API
```

**Timeline:**
1. **0s**: Mobile app requests video generation
2. **0s**: Backend calls AI service (receives job_id immediately)
3. **0s**: Backend returns job_id to app (user sees "Processing...")
4. **0-5s**: AI service validates pets, translates text
5. **5-60s**: Revid.ai generates video (async)
6. **60s**: AI service receives webhook from Revid
7. **60s**: AI service webhooks your backend
8. **60s**: Backend sends push notification to user
9. **60s**: User sees "Video ready!" notification

---

## Testing

### 1. Health Check
```bash
curl https://your-ai-service.railway.app/healthz
```

### 2. Backend Connection
```bash
curl https://your-ai-service.railway.app/api/test-backend-connection
```

### 3. Generate Video
```bash
curl -X POST https://your-ai-service.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my lazy dog!",
    "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
  }'
```

### 4. Check Status
```bash
curl https://your-ai-service.railway.app/api/video-status/{job_id}
```

### 5. Integration Test Suite
```bash
python test_integration.py \
  --ai-service-url https://your-ai-service.railway.app \
  --backend-url https://your-backend.railway.app
```

---

## Support

For issues:
1. Check Railway logs: `railway logs`
2. Verify environment variables are set
3. Test backend connectivity: `GET /api/test-backend-connection`
4. Run integration tests: `python test_integration.py`

---

**Version:** 1.0.0
**Last Updated:** December 7, 2025
