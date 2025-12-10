# 🎬 Pet Roast AI Service

> AI-powered pet roasting service with YOLOv5 pet detection, multi-language support, and video generation.

[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-blueviolet)](https://railway.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)

## 🚀 Quick Deploy to Railway

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy AI service"
git push origin main

# 2. Deploy on Railway
# - Go to https://railway.app
# - New Project → Deploy from GitHub
# - Select this repository
# - Railway auto-detects Dockerfile
```

**See full guide:** [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

## 📁 Project Structure

```
pet_roasts/
├── app/
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── services/
│   │   ├── pet_detection.py       # YOLOv5 detection
│   │   └── job_store.py           # Job management
│   ├── clients/
│   │   ├── revid.py               # Video generation
│   │   └── ai4bharat.py           # Translation
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   └── webhook.py             # Webhook utilities
│   └── main.py                    # FastAPI app
│
├── Dockerfile                      # Railway deployment
├── railway.json                    # Railway config
├── requirements.txt                # Dependencies
└── .env.railway                    # Environment template
```

## 🎯 API Endpoints

### Health Check
```bash
GET /healthz
```

### Generate Video (with Pet Detection)
```bash
POST /api/generate-video
Content-Type: application/json

{
  "text": "Roast my lazy dog!",
  "image_url": "https://example.com/dog.jpg"
}

Response:
{
  "job_id": "abc123",
  "status": "processing"
}
```

### Check Video Status
```bash
GET /api/video-status/{job_id}

Response:
{
  "job_id": "abc123",
  "status": "completed",
  "video_url": "https://...",
  "created_at": "2025-12-07T10:00:00Z"
}
```

### Webhook (Called by Revid when video is ready)
```bash
POST /api/webhook/video-complete

{
  "job_id": "abc123",
  "status": "completed",
  "video_url": "https://..."
}
```

## 🔧 Configuration

Required environment variables:

```env
# Revid.ai API (REQUIRED)
REVID_API_KEY=your_revid_api_key

# Backend webhook (Your Railway backend URL)
BACKEND_WEBHOOK_URL=https://your-backend.railway.app/webhooks/pet-roast-complete

# CORS origins
CORS_ORIGINS=["https://your-backend.railway.app"]

# Redis (Use Railway addon)
REDIS_URL=redis://default:password@redis.railway.internal:6379
USE_REDIS=true
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Mobile App / Frontend                           │
└────────────────────────┬────────────────────────────────────┘
                         │ GraphQL
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Backend (Railway)                                    │
│         https://your-backend.railway.app                     │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API POST /api/generate-video
                 ▼
┌─────────────────────────────────────────────────────────────┐
│       Pet Roast AI (Railway) - THIS SERVICE                  │
│       https://your-ai-service.up.railway.app                 │
│                                                              │
│  1. Pet Detection (YOLOv5)        ✓                         │
│  2. Translation (AI4Bharat)       ✓                         │
│  3. Video Generation (Revid.ai)   ✓                         │
│  4. Webhook Backend               ✓                         │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─→ Redis (Job Queue)
       └─→ Revid.ai API
```

## ✨ Features

- ✅ **Pet Detection** - YOLOv5 validates pets before processing
- ✅ **Multi-language** - AI4Bharat/IndicTrans2 translation support
- ✅ **Video Generation** - Revid.ai integration
- ✅ **Job Queue** - Redis-backed persistent storage
- ✅ **Webhook Support** - Notifies backend when video is ready
- ✅ **Health Monitoring** - Built-in health checks
- ✅ **CORS Configured** - Ready for frontend integration
- ✅ **Railway Ready** - Optimized for Railway deployment

## 🧪 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.railway .env
# Edit .env with your keys

# Run locally
uvicorn app.main:app --reload --port 8000

# Test
curl http://localhost:8000/healthz
```

## 🔗 Testing Integration

Test the complete integration between AI service and backend:

```bash
# Install test dependencies (if not already installed)
pip install httpx

# Run integration tests
python test_integration.py \
  --ai-service-url https://your-ai-service.railway.app \
  --backend-url https://your-backend.railway.app \
  --test-image https://example.com/dog.jpg
```

The test suite will verify:
- ✅ AI service health
- ✅ Backend connectivity
- ✅ Pet detection
- ✅ Video generation
- ✅ Webhook delivery

## 📊 Monitoring

### View Logs (Railway)
```bash
railway logs
```

### Check Status
```bash
railway status
```

## 🐛 Troubleshooting

### No Pets Detected Error
- Ensure image contains clear pet photos
- Supported: dog, cat, bird, horse, sheep, cow, elephant, bear, zebra, giraffe

### Backend Not Receiving Webhook
- Verify `BACKEND_WEBHOOK_URL` is set correctly
- Check backend webhook endpoint is accessible
- Review logs: `railway logs`

### Redis Connection Failed
- Add Redis addon in Railway dashboard
- Check `REDIS_URL` is set automatically

## 🔗 Integration with Backend

Your Railway backend should call this service:

```typescript
// In your backend service
const response = await fetch('https://your-ai-service.up.railway.app/api/generate-video', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Roast my pet!',
    image_url: petImageUrl
  })
});

const { job_id } = await response.json();
// Store job_id, AI service will webhook when done
```

Backend webhook handler:
```typescript
// POST /webhooks/pet-roast-complete
app.post('/webhooks/pet-roast-complete', async (req, res) => {
  const { job_id, status, video_url } = req.body;
  // Update database with video_url
  // Notify user via push notification
});
```

## 📚 Documentation

### 🎯 Getting Started
- [QUICK_START_BACKEND.md](QUICK_START_BACKEND.md) - **5-minute backend integration guide**
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Complete Railway deployment guide

### 🔗 Integration
- [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) - **Full backend integration (Node.js/GraphQL)**
- [API_REFERENCE.md](API_REFERENCE.md) - **Complete API documentation**

### 📖 Reference
- [SETUP.md](SETUP.md) - Detailed setup instructions
- [COMMANDS.md](COMMANDS.md) - Command reference

## 🚀 Production Checklist

- [ ] Deploy to Railway
- [ ] Set all environment variables
- [ ] Add Redis addon
- [ ] Configure backend webhook URL
- [ ] Test pet detection endpoint
- [ ] Test video generation flow
- [ ] Verify webhook callbacks work
- [ ] Set up monitoring/alerts

## 📝 License

Private project for PetSnapChat application.

---

## 🎊 What's New

**Latest Update:** Perfect Backend Integration (Dec 7, 2025)

- ✅ **Robust Webhook System** - 3 retry attempts with exponential backoff
- ✅ **Backend Connectivity Testing** - Test endpoint for verifying backend connection
- ✅ **Comprehensive Documentation** - 2,400+ lines of guides and examples
- ✅ **Integration Test Suite** - Automated testing for complete flow
- ✅ **Setup Scripts** - Interactive configuration wizard
- ✅ **Complete API Reference** - Full documentation with code examples

---

**Version:** 2.0.0 - Perfect Backend Integration
**Last Updated:** December 7, 2025
**Status:** ✅ Production Ready for Railway Deployment
