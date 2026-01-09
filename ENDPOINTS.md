# 🔌 API Endpoints Reference - Quick Guide

## 🌐 Base URLs

```
AI Service (After Railway Deployment):
https://your-ai-service-name.up.railway.app

Local Development:
http://localhost:8000
```

---

## 📍 All Available Endpoints

### 1. Health Check ✅
Check if service is running

```http
GET /healthz
```

**Response:**
```json
{
  "status": "ok"
}
```

**cURL:**
```bash
curl https://your-ai-service.railway.app/healthz
```

---

### 2. Test Backend Connection 🔗
Test connectivity to your backend

```http
GET /api/test-backend-connection
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Backend is reachable",
  "backend_url": "https://your-backend.railway.app/api/webhooks/video-complete",
  "response_code": 200,
  "response_time_ms": 145.23
}
```

**Response (Not Configured):**
```json
{
  "status": "not_configured",
  "message": "BACKEND_WEBHOOK_URL not set",
  "backend_url": null
}
```

**cURL:**
```bash
curl https://your-ai-service.railway.app/api/test-backend-connection
```

---

### 3. Generate Video 🎬
Create a pet roast video with AI

```http
POST /api/generate-video
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Roast my lazy dog who sleeps all day!",
  "image_url": "https://example.com/dog-image.jpg"
}
```

**Response (200):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "processing",
  "message": "Video generation started",
  "created_at": "2026-01-09T10:30:00Z"
}
```

**Response (400 - No Pet Detected):**
```json
{
  "detail": "No pet detected in the image. Please upload an image with a visible pet."
}
```

**Response (502 - Service Error):**
```json
{
  "detail": "Failed to communicate with video generation service"
}
```

**cURL:**
```bash
curl -X POST https://your-ai-service.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my lazy dog",
    "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
  }'
```

**JavaScript (Axios):**
```javascript
const response = await axios.post(
  'https://your-ai-service.railway.app/api/generate-video',
  {
    text: 'Roast my lazy dog',
    image_url: 'https://example.com/dog.jpg'
  }
);

const { job_id, status } = response.data;
console.log(`Job created: ${job_id}`);
```

**Python (Requests):**
```python
import requests

response = requests.post(
    'https://your-ai-service.railway.app/api/generate-video',
    json={
        'text': 'Roast my lazy dog',
        'image_url': 'https://example.com/dog.jpg'
    }
)

data = response.json()
print(f"Job ID: {data['job_id']}")
```

---

### 4. Check Video Status 📊
Poll for video generation progress

```http
GET /api/video-status/{job_id}
```

**Response (Processing):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "processing",
  "created_at": "2026-01-09T10:30:00Z",
  "updated_at": "2026-01-09T10:30:15Z"
}
```

**Response (Completed):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "completed",
  "video_url": "https://cdn.revid.ai/videos/abc-123-xyz-789.mp4",
  "created_at": "2026-01-09T10:30:00Z",
  "completed_at": "2026-01-09T10:31:25Z"
}
```

**Response (Failed):**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "failed",
  "error": "Video generation failed",
  "created_at": "2026-01-09T10:30:00Z"
}
```

**Response (404 - Not Found):**
```json
{
  "detail": "Job not found"
}
```

**cURL:**
```bash
curl https://your-ai-service.railway.app/api/video-status/abc-123-xyz-789
```

**JavaScript (Polling):**
```javascript
async function pollVideoStatus(jobId) {
  const maxAttempts = 30; // 30 attempts
  const pollInterval = 2000; // 2 seconds

  for (let i = 0; i < maxAttempts; i++) {
    const response = await axios.get(
      `https://your-ai-service.railway.app/api/video-status/${jobId}`
    );

    const { status, video_url } = response.data;

    if (status === 'completed') {
      console.log('Video ready:', video_url);
      return video_url;
    } else if (status === 'failed') {
      throw new Error('Video generation failed');
    }

    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }

  throw new Error('Polling timeout');
}
```

---

### 5. Get Video Result 🎥
Get final video URL (alternative to status check)

```http
GET /api/video-result/{job_id}
```

**Response (200):**
```json
{
  "job_id": "abc-123-xyz-789",
  "video_url": "https://cdn.revid.ai/videos/abc-123-xyz-789.mp4",
  "status": "completed",
  "completed_at": "2026-01-09T10:31:25Z"
}
```

**Response (404):**
```json
{
  "detail": "Video not ready or job not found"
}
```

**cURL:**
```bash
curl https://your-ai-service.railway.app/api/video-result/abc-123-xyz-789
```

---

### 6. Webhook (Video Complete) 🔔
**Called by AI service to notify your backend**

```http
POST /api/webhook/video-complete
Content-Type: application/json
```

**Request Body:**
```json
{
  "job_id": "abc-123-xyz-789",
  "status": "completed",
  "video_url": "https://cdn.revid.ai/videos/abc-123-xyz-789.mp4",
  "user_id": "user-456",
  "metadata": {
    "duration": 15.5,
    "resolution": "1080p"
  }
}
```

**Your Backend Must Respond:**
```json
{
  "success": true,
  "message": "Webhook received"
}
```

**⚠️ Important:** This endpoint is called BY the AI service TO your backend, not the other way around!

---

### 7. Translate Text 🌐
Translate text to Indian languages

```http
POST /api/translate-text
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Your pet is adorable!",
  "source_lang": "en",
  "target_lang": "hi",
  "task": "translation"
}
```

**Supported Languages:**
- `en` - English
- `hi` - Hindi
- `bn` - Bengali
- `gu` - Gujarati
- `mr` - Marathi
- `kn` - Kannada
- `te` - Telugu
- `ml` - Malayalam
- `ta` - Tamil
- `pa` - Punjabi
- `or` - Odia
- `as` - Assamese
- `ur` - Urdu

**Response:**
```json
{
  "translated_text": "आपका पालतू जानवर बहुत प्यारा है!",
  "source_language": "en",
  "target_language": "hi"
}
```

**cURL:**
```bash
curl -X POST https://your-ai-service.railway.app/api/translate-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your pet is adorable!",
    "source_lang": "en",
    "target_lang": "hi"
  }'
```

---

### 8. List Banuba Filters 🎨
Get available AR filters

```http
GET /api/banuba-filters
```

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

**cURL:**
```bash
curl https://your-ai-service.railway.app/api/banuba-filters
```

---

### 9. API Documentation 📚
Interactive API documentation

```http
GET /docs
```

Opens Swagger UI with interactive API testing

**URL:**
```
https://your-ai-service.railway.app/docs
```

---

### 10. OpenAPI Schema 📋
Get OpenAPI/Swagger JSON schema

```http
GET /openapi.json
```

**Response:** Full OpenAPI 3.0 specification

**cURL:**
```bash
curl https://your-ai-service.railway.app/openapi.json
```

---

## 🔄 Complete User Flow Example

### Step-by-Step Integration

```javascript
// 1. User uploads image to your backend
const formData = new FormData();
formData.append('image', imageFile);

const uploadResponse = await axios.post(
  'https://your-backend.railway.app/api/upload',
  formData
);

const imageUrl = uploadResponse.data.imageUrl;

// 2. Backend calls AI service to generate video
const generateResponse = await axios.post(
  'https://your-ai-service.railway.app/api/generate-video',
  {
    text: roastText,
    image_url: imageUrl
  }
);

const jobId = generateResponse.data.job_id;

// 3. Save job_id to your database
await db.videos.create({
  jobId: jobId,
  userId: userId,
  status: 'processing',
  imageUrl: imageUrl
});

// 4. Return job_id to frontend
res.json({ jobId: jobId, status: 'processing' });

// 5. Frontend polls for status (or wait for webhook)
const pollStatus = async () => {
  const statusResponse = await axios.get(
    `https://your-ai-service.railway.app/api/video-status/${jobId}`
  );

  if (statusResponse.data.status === 'completed') {
    const videoUrl = statusResponse.data.video_url;
    // Show video to user
    displayVideo(videoUrl);
  } else if (statusResponse.data.status === 'processing') {
    // Wait 2 seconds and poll again
    setTimeout(pollStatus, 2000);
  } else {
    // Handle error
    showError('Video generation failed');
  }
};

pollStatus();

// 6. Meanwhile, AI service will call your webhook when done
// Your webhook at: POST /api/webhooks/video-complete
// Will receive: { job_id, status, video_url }
// You can then send push notification to user
```

---

## 🛡️ Error Codes

| Status Code | Meaning | Common Cause |
|------------|---------|--------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input data or no pet detected |
| 404 | Not Found | Job ID not found |
| 422 | Validation Error | Request body validation failed |
| 502 | Bad Gateway | External service (Revid.ai) failed |
| 503 | Service Unavailable | Service is starting or overloaded |

---

## 🔧 Testing Tools

### Postman Collection
Import the provided `postman_collection.json` for easy testing

### cURL Scripts
Test all endpoints quickly:

```bash
# Set your base URL
export API_URL="https://your-ai-service.railway.app"

# Test health
curl $API_URL/healthz

# Test backend connection
curl $API_URL/api/test-backend-connection

# Generate video
curl -X POST $API_URL/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text":"Test","image_url":"https://images.unsplash.com/photo-1543466835-00a7907e9de1"}'

# Check status (replace JOB_ID)
curl $API_URL/api/video-status/YOUR_JOB_ID
```

---

## 📱 Backend Routes You Need

Your backend must implement:

```
POST /api/webhooks/video-complete  ← AI service calls this
POST /api/upload                    ← User uploads image
POST /api/roast/generate            ← Calls AI service
GET  /api/roast/status/:jobId       ← Frontend polls this
```

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│ GENERATE VIDEO                                              │
│ POST /api/generate-video                                    │
│ Body: {"text":"...", "image_url":"..."}                     │
│ Returns: {"job_id":"...", "status":"processing"}            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CHECK STATUS                                                │
│ GET /api/video-status/{job_id}                              │
│ Returns: {"status":"completed", "video_url":"..."}          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ WEBHOOK (Your Backend Receives)                            │
│ POST /api/webhooks/video-complete                           │
│ Body: {"job_id":"...", "status":"...", "video_url":"..."}   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Ready to Use!

All endpoints are ready after Railway deployment. Just update:
- `your-ai-service.railway.app` with your actual Railway URL
- Configure environment variables as per DEPLOY_AND_CONNECT.md

**Happy Coding! 🎉**
