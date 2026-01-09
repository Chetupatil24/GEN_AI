# 🚀 Complete Deployment & Connection Guide

## Step-by-Step Guide to Deploy AI Service and Connect to Backend

---

## 📋 Prerequisites

1. **Railway Account** - Sign up at https://railway.app
2. **GitHub Repository** - Already pushed ✅
3. **Revid.ai API Key** - Get from https://revid.ai
4. **Backend Already Deployed** - Your backend URL on Railway

---

## 🎯 Architecture Overview

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│  Your Backend   │◄────────┤   AI Service    │────────►│   Revid.ai      │
│   (Railway)     │ Webhook │   (Railway)     │  API    │   (External)    │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         ▲                           ▲
         │                           │
         │                           ├───► Redis (Railway)
         │                           │
         └───────────────────────────┘
              Job Status Updates
```

---

## 📦 Part 1: Deploy AI Service to Railway

### Option A: Deploy via Railway Dashboard (Recommended)

#### Step 1: Create New Project
1. Go to https://railway.app/dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select repository: **Chetupatil24/GEN_AI**
6. Railway will automatically detect the **Dockerfile**

#### Step 2: Add Redis Database
1. In your project, click **"+ New"**
2. Select **"Database"** → **"Add Redis"**
3. Railway automatically creates `REDIS_URL` environment variable
4. Copy the Redis URL (looks like: `redis://default:xxx@containers-us-west-xxx.railway.app:7393`)

#### Step 3: Configure Environment Variables
1. Click on your AI Service
2. Go to **"Variables"** tab
3. Add these variables:

```env
# Required Variables
REVID_API_KEY=your_actual_revid_api_key_here
BACKEND_WEBHOOK_URL=https://your-backend-name.up.railway.app/api/webhooks/video-complete
REDIS_URL=redis://default:xxx@containers-us-west-xxx.railway.app:7393
USE_REDIS=true

# CORS Configuration (Add your backend URL)
CORS_ORIGINS=["https://your-backend-name.up.railway.app"]

# Optional but Recommended
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
REDIS_JOB_TTL_SECONDS=604800
```

#### Step 4: Deploy
1. Railway will automatically deploy after you save variables
2. Wait for deployment to complete (2-5 minutes)
3. Your AI service URL will be: `https://your-ai-service-name.up.railway.app`

---

### Option B: Deploy via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project (or create new)
railway link

# Set environment variables
railway variables set REVID_API_KEY=your_key_here
railway variables set BACKEND_WEBHOOK_URL=https://your-backend.railway.app/api/webhooks/video-complete
railway variables set USE_REDIS=true
railway variables set CORS_ORIGINS='["https://your-backend.railway.app"]'

# Deploy
railway up

# Get your service URL
railway domain
```

---

## 🔗 Part 2: Connect Backend to AI Service

### Backend Configuration

In your **Backend Railway Project**, add these environment variables:

```env
# AI Service URL
PET_ROAST_AI_URL=https://your-ai-service-name.up.railway.app

# Optional: API Key (if you add authentication later)
PET_ROAST_AI_KEY=your_api_key_here
```

---

## 🛠️ Part 3: Backend Implementation

### Required Backend Endpoints

#### 1. Webhook Endpoint (MUST IMPLEMENT)

Your backend needs to handle video completion notifications from the AI service.

**Endpoint:** `POST /api/webhooks/video-complete`

**Example Implementation (Node.js/Express):**

```javascript
// backend/routes/webhooks.js
const express = require('express');
const router = express.Router();

router.post('/video-complete', async (req, res) => {
  try {
    const { job_id, status, video_url, user_id, error } = req.body;

    console.log('Video webhook received:', { job_id, status });

    if (status === 'completed' && video_url) {
      // Update your database
      await db.videos.update({
        where: { jobId: job_id },
        data: {
          status: 'completed',
          videoUrl: video_url,
          completedAt: new Date()
        }
      });

      // Send push notification to user
      if (user_id) {
        await sendPushNotification(user_id, {
          title: 'Your Pet Roast is Ready! 🎉',
          body: 'Your hilarious pet roast video is ready to watch!',
          data: { videoUrl: video_url, jobId: job_id }
        });
      }

      res.json({ success: true, message: 'Webhook processed' });
    } else if (status === 'failed') {
      // Handle failure
      await db.videos.update({
        where: { jobId: job_id },
        data: {
          status: 'failed',
          error: error || 'Video generation failed'
        }
      });

      res.json({ success: true, message: 'Failure recorded' });
    }
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

module.exports = router;
```

**Example Implementation (Python/FastAPI):**

```python
# backend/routes/webhooks.py
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

router = APIRouter()

class VideoWebhook(BaseModel):
    job_id: str
    status: str
    video_url: str | None = None
    user_id: str | None = None
    error: str | None = None

@router.post("/webhooks/video-complete")
async def video_complete_webhook(webhook: VideoWebhook, background_tasks: BackgroundTasks):
    """Handle video completion webhook from AI service"""

    if webhook.status == "completed" and webhook.video_url:
        # Update database
        await db.videos.update(
            job_id=webhook.job_id,
            status="completed",
            video_url=webhook.video_url
        )

        # Send push notification
        if webhook.user_id:
            background_tasks.add_task(
                send_push_notification,
                webhook.user_id,
                title="Your Pet Roast is Ready! 🎉",
                body="Your hilarious pet roast video is ready!",
                data={"videoUrl": webhook.video_url, "jobId": webhook.job_id}
            )

    elif webhook.status == "failed":
        await db.videos.update(
            job_id=webhook.job_id,
            status="failed",
            error=webhook.error or "Video generation failed"
        )

    return {"success": True, "message": "Webhook processed"}
```

---

#### 2. API Call from Backend to AI Service

**Example: Trigger Video Generation from Your Backend**

```javascript
// backend/services/petRoastService.js
const axios = require('axios');

class PetRoastService {
  constructor() {
    this.aiServiceUrl = process.env.PET_ROAST_AI_URL;
  }

  async generateRoastVideo(text, imageUrl, userId) {
    try {
      // Call AI service
      const response = await axios.post(
        `${this.aiServiceUrl}/api/generate-video`,
        {
          text: text,
          image_url: imageUrl
        },
        {
          timeout: 30000,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      const { job_id, status } = response.data;

      // Save to your database
      await db.videos.create({
        jobId: job_id,
        userId: userId,
        status: status,
        imageUrl: imageUrl,
        roastText: text,
        createdAt: new Date()
      });

      return {
        success: true,
        jobId: job_id,
        status: status,
        message: 'Video generation started'
      };

    } catch (error) {
      console.error('AI service error:', error);
      throw new Error('Failed to generate video');
    }
  }

  async getVideoStatus(jobId) {
    try {
      const response = await axios.get(
        `${this.aiServiceUrl}/api/video-status/${jobId}`
      );

      return response.data;
    } catch (error) {
      console.error('Status check error:', error);
      return { status: 'unknown', error: error.message };
    }
  }
}

module.exports = new PetRoastService();
```

---

## 📡 Complete API Integration Flow

### Flow Diagram:

```
1. User uploads pet image to backend
   ↓
2. Backend → POST to AI Service: /api/generate-video
   {
     "text": "Roast my lazy dog",
     "image_url": "https://your-backend.railway.app/uploads/dog.jpg"
   }
   ↓
3. AI Service responds immediately:
   {
     "job_id": "abc-123-xyz",
     "status": "processing"
   }
   ↓
4. Backend saves job_id to database
   ↓
5. Backend → Returns to user:
   {
     "success": true,
     "jobId": "abc-123-xyz",
     "message": "Video is being generated"
   }
   ↓
6. AI Service processes video (30-60 seconds)
   - Downloads image
   - Detects pet with YOLOv5
   - Calls Revid.ai
   ↓
7. AI Service → Webhook to Backend: /api/webhooks/video-complete
   {
     "job_id": "abc-123-xyz",
     "status": "completed",
     "video_url": "https://cdn.revid.ai/videos/abc-123.mp4"
   }
   ↓
8. Backend updates database
   ↓
9. Backend sends push notification to user
   ↓
10. User gets notification with video URL
```

---

## 🔐 Security Best Practices

### 1. Add Webhook Secret Validation

Update your backend webhook to verify requests:

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(JSON.stringify(payload))
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

router.post('/video-complete', async (req, res) => {
  const signature = req.headers['x-webhook-signature'];
  const secret = process.env.WEBHOOK_SECRET;

  if (!verifyWebhookSignature(req.body, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process webhook...
});
```

### 2. Add API Key Authentication (Optional)

```javascript
// Middleware for AI service calls
function requireApiKey(req, res, next) {
  const apiKey = req.headers['x-api-key'];

  if (apiKey !== process.env.AI_SERVICE_API_KEY) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  next();
}

router.post('/generate-video', requireApiKey, async (req, res) => {
  // Handle request...
});
```

---

## 🧪 Testing the Integration

### Test 1: Check AI Service Health

```bash
curl https://your-ai-service-name.up.railway.app/healthz
# Expected: {"status":"ok"}
```

### Test 2: Test Backend Connection

```bash
curl https://your-ai-service-name.up.railway.app/api/test-backend-connection
# Should show connection status to your backend
```

### Test 3: Generate Test Video

```bash
curl -X POST https://your-ai-service-name.up.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test roast",
    "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
  }'

# Expected: {"job_id":"xxx-yyy-zzz","status":"processing"}
```

### Test 4: Check Video Status

```bash
curl https://your-ai-service-name.up.railway.app/api/video-status/xxx-yyy-zzz

# Expected: {"job_id":"xxx-yyy-zzz","status":"completed","video_url":"..."}
```

### Test 5: Verify Webhook Received

Check your backend logs to confirm webhook was received and processed.

---

## 📊 Monitoring & Logs

### View AI Service Logs

```bash
# Via Railway CLI
railway logs

# Or view in Railway Dashboard → Your Service → Deployments → Logs
```

### Common Log Messages

```
✅ Application startup complete
✅ Using Redis for persistent job storage
✅ YOLO model loaded successfully
⚠️  Redis connection failed: Falling back to in-memory storage
❌ Failed to notify backend webhook
```

---

## 🆘 Troubleshooting

### Issue 1: "Failed to notify backend webhook"

**Cause:** Backend URL is incorrect or backend is not responding

**Solution:**
1. Check `BACKEND_WEBHOOK_URL` in Railway variables
2. Verify backend endpoint exists: `POST /api/webhooks/video-complete`
3. Check backend logs for errors
4. Test backend directly:
```bash
curl -X POST https://your-backend.railway.app/api/webhooks/video-complete \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test","status":"completed","video_url":"https://test.com/video.mp4"}'
```

### Issue 2: "CORS Error" in Frontend

**Cause:** Backend URL not in CORS_ORIGINS

**Solution:**
```bash
railway variables set CORS_ORIGINS='["https://your-backend.railway.app","https://your-frontend.railway.app"]'
```

### Issue 3: Redis Connection Failed

**Cause:** Redis not properly configured

**Solution:**
1. Verify Redis addon is added in Railway
2. Copy the `REDIS_URL` from Redis service
3. Update AI service with correct `REDIS_URL`
4. Redeploy

### Issue 4: Video Generation Fails

**Cause:** Invalid Revid.ai API key or image URL

**Solution:**
1. Verify `REVID_API_KEY` is correct
2. Ensure image URL is publicly accessible
3. Check Revid.ai dashboard for API status
4. Review logs: `railway logs`

---

## 🎯 Environment Variables Checklist

### AI Service (Required)

- [x] `REVID_API_KEY` - Your Revid.ai API key
- [x] `BACKEND_WEBHOOK_URL` - Your backend webhook URL
- [x] `REDIS_URL` - Redis connection string
- [x] `USE_REDIS` - Set to `true`
- [x] `CORS_ORIGINS` - JSON array of allowed origins

### Backend (Required)

- [x] `PET_ROAST_AI_URL` - Your AI service URL
- [x] Webhook endpoint implemented at `/api/webhooks/video-complete`

---

## 📱 Complete Backend Routes Required

```javascript
// 1. Generate video (called by your app)
POST /api/roast/generate
Body: { text, imageUrl, userId }
Response: { jobId, status }

// 2. Check video status (polled by frontend)
GET /api/roast/status/:jobId
Response: { jobId, status, videoUrl }

// 3. Webhook endpoint (called by AI service)
POST /api/webhooks/video-complete
Body: { job_id, status, video_url, user_id }
Response: { success: true }
```

---

## 🚀 Next Steps

1. ✅ Deploy AI service to Railway
2. ✅ Add Redis to AI service project
3. ✅ Configure environment variables
4. ✅ Implement webhook endpoint in backend
5. ✅ Add AI service URL to backend
6. ✅ Test the complete flow
7. ✅ Monitor logs for any errors
8. ✅ Add error handling in backend
9. ✅ Implement push notifications
10. ✅ Test with real users

---

## 📞 Support

- **Railway Docs:** https://docs.railway.app
- **Revid.ai Docs:** https://docs.revid.ai
- **FastAPI Docs:** https://fastapi.tiangolo.com

---

## 🎉 Success Criteria

Your integration is successful when:

✅ AI service deploys without errors
✅ Health check returns `{"status":"ok"}`
✅ Backend connection test passes
✅ Video generation creates job_id
✅ Webhook reaches backend successfully
✅ Backend updates database with video URL
✅ User receives push notification
✅ Video plays in app

**You're Ready to Go! 🚀**
