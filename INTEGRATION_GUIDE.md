# 🚀 Quick Start - Backend Integration

## ✅ Complete Setup Checklist

Your Pet Roast AI project is now **production-ready** with the following features:

### ✨ New Features Added

1. **🐕 Pet Detection** - Automatically validates pet presence before video generation
2. **🔗 Backend Integration** - Complete POC and client library for Snapchat-like apps
3. **📚 Documentation** - Comprehensive API guide with examples
4. **🐳 Docker Support** - Production-ready containerization
5. **♻️ Retry Logic** - Automatic retry with exponential backoff

---

## 📦 Project Structure

```
pet_roasts/
├── app/                          # FastAPI backend
│   ├── api/routes.py            # API endpoints (now with pet detection)
│   ├── services/
│   │   ├── pet_detection.py     # 🆕 YOLO-based pet detection
│   │   ├── job_store.py         # Job management
│   │   └── redis_job_store.py   # Redis persistence
│   ├── clients/                 # External API clients
│   └── core/                    # Config & utilities
├── examples/
│   └── backend_client.py        # 🆕 Production-ready client library
├── IndicTrans2/                 # Translation model
├── BACKEND_INTEGRATION.md       # 🆕 Complete integration guide
├── docker-compose.yml           # 🆕 Docker orchestration
├── Dockerfile                   # 🆕 API container
└── requirements.txt             # Updated with CV dependencies
```

---

## 🎯 How to Connect to Your Backend

### Step 1: Start the Services

```bash
# Clone the repository (if not already done)
git clone https://github.com/petroastapp-ai/GEN_AI.git
cd GEN_AI

# Set up environment variables
cp .env.example .env
# Edit .env and add your REVID_API_KEY

# Start all services with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:8000/healthz
```

### Step 2: Test Pet Detection

```bash
# Test with a pet image (should succeed)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast my lazy dog",
    "image_url": "https://images.dog.ceo/breeds/husky/n02110185_10047.jpg"
  }'

# Test with non-pet image (should fail with 400)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Roast this",
    "image_url": "https://example.com/car.jpg"
  }'
# Response: {"detail": {"error": "no_pets_detected", "message": "No pets found..."}}
```

### Step 3: Integrate with Your Backend

#### Option A: Use the Python Client Library

```python
# In your Snapchat-like backend
from examples.backend_client import PetRoastClient

async def handle_pet_roast_request(user_id: str, image_url: str, prompt: str):
    async with PetRoastClient(base_url="http://pet-roast-api:8000") as client:
        result = await client.generate_video_with_retry(
            image_url=image_url,
            prompt=prompt
        )

        if result["success"]:
            # Save to your database
            await db.posts.create({
                "user_id": user_id,
                "job_id": result["job_id"],
                "video_url": result["video_url"],
                "status": "completed"
            })
            return result["video_url"]
        else:
            # Handle error (no pets detected, etc.)
            return {"error": result["error"], "message": result["message"]}
```

#### Option B: Direct HTTP Calls

```javascript
// In your Node.js/Express backend
const axios = require('axios');

async function generatePetRoast(imageUrl, prompt) {
  try {
    // Step 1: Generate video
    const response = await axios.post('http://pet-roast-api:8000/api/generate-video', {
      text: prompt,
      image_url: imageUrl
    });

    const { job_id } = response.data;

    // Step 2: Poll for completion
    while (true) {
      const status = await axios.get(`http://pet-roast-api:8000/api/video-status/${job_id}`);

      if (status.data.status === 'completed') {
        const result = await axios.get(`http://pet-roast-api:8000/api/video-result/${job_id}`);
        return { success: true, videoUrl: result.data.video_url };
      } else if (status.data.status === 'failed') {
        return { success: false, error: 'Video generation failed' };
      }

      await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5s
    }
  } catch (error) {
    if (error.response?.status === 400) {
      return {
        success: false,
        error: 'no_pets_detected',
        message: error.response.data.detail.message
      };
    }
    throw error;
  }
}
```

---

## 🔗 API Endpoints Summary

| Endpoint | Method | Purpose | Pet Detection |
|----------|--------|---------|---------------|
| `/healthz` | GET | Health check | ❌ |
| `/api/translate-text` | POST | Translate text | ❌ |
| `/api/generate-video` | POST | Generate roast video | ✅ **Yes** |
| `/api/video-status/{job_id}` | GET | Check status | ❌ |
| `/api/video-result/{job_id}` | GET | Get video URL | ❌ |
| `/api/banuba-filters` | GET | List AR filters | ❌ |

---

## 🐕 Pet Detection Logic

**Supported Pets:**
- 🐕 Dogs
- 🐈 Cats
- 🐦 Birds
- 🐴 Horses
- 🐑 Sheep
- 🐄 Cows
- 🐘 Elephants
- 🐻 Bears
- 🦓 Zebras
- 🦒 Giraffes

**Detection Method:**
- Uses **YOLOv5** for object detection
- Minimum confidence: **50%**
- Validates before API calls (saves costs!)

**Error Handling:**
```json
// No pets detected
{
  "detail": {
    "error": "no_pets_detected",
    "message": "No pets found in the uploaded image. Please upload an image or video containing pets.",
    "suggestion": "Try uploading a clear photo or video of your pet."
  }
}
```

---

## 📚 Documentation

- **[BACKEND_INTEGRATION.md](./BACKEND_INTEGRATION.md)** - Complete integration guide
- **[examples/backend_client.py](./examples/backend_client.py)** - Production-ready client
- **[README.md](./README.md)** - Original project documentation

---

## 🚀 Deployment Options

### 1. Docker Compose (Recommended for POC)

```bash
docker-compose up -d
```

**Services started:**
- `pet-roast-api` (port 8000) - Main API
- `redis` (port 6379) - Job storage
- `indictrans2` (port 5000) - Translation service
- `streamlit-ui` (port 8501) - Test UI

### 2. Kubernetes (Production)

See `BACKEND_INTEGRATION.md` for Kubernetes deployment YAML.

### 3. Cloud Run / AWS ECS

Deploy the Docker image to your cloud provider:

```bash
# Build image
docker build -t pet-roast-ai:latest .

# Tag for your registry
docker tag pet-roast-ai:latest your-registry.com/pet-roast-ai:latest

# Push
docker push your-registry.com/pet-roast-ai:latest
```

---

## 🔐 Environment Variables

Create a `.env` file:

```bash
# Required
REVID_API_KEY=your_revid_api_key_here
REVID_WEBHOOK_SECRET=your_webhook_secret_here

# Optional (defaults provided)
AI4BHARAT_BASE_URL=http://localhost:5000
REDIS_URL=redis://localhost:6379/0
USE_REDIS=true
```

---

## 🧪 Testing

### Test Pet Detection

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/test_api.py -v

# Test pet detection specifically
python -m app.services.pet_detection
```

### Manual Testing

```bash
# Test with dog image (should work)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "Roast my dog", "image_url": "https://images.dog.ceo/breeds/husky/n02110185_10047.jpg"}'

# Test with cat image (should work)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "Roast my cat", "image_url": "https://cataas.com/cat"}'

# Test with non-pet (should fail)
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"text": "Roast this", "image_url": "https://picsum.photos/200"}'
```

---

## 📊 Architecture

```
┌──────────────────────────────────────────────────────────┐
│           Your Snapchat-like Backend                     │
│  (Node.js / Python / Go)                                 │
└────────────────┬─────────────────────────────────────────┘
                 │ HTTP/REST
                 ▼
┌──────────────────────────────────────────────────────────┐
│           Pet Roast AI Microservice                      │
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │    Pet     │→ │Translation │→ │   Video    │        │
│  │ Detection  │  │(AI4Bharat) │  │(Revid.ai)  │        │
│  │  (YOLO)    │  │            │  │            │        │
│  └────────────┘  └────────────┘  └────────────┘        │
│                                                           │
│  ┌────────────┐  ┌────────────┐                         │
│  │   Redis    │  │  Webhook   │                         │
│  │   Store    │  │  Handler   │                         │
│  └────────────┘  └────────────┘                         │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ POC Validation Checklist

- [x] **Pet detection working** - YOLO detects dogs, cats, etc.
- [x] **API endpoints functional** - All endpoints responding
- [x] **Error handling** - Graceful failures with clear messages
- [x] **Client library** - Python client with retry logic
- [x] **Documentation** - Complete integration guide
- [x] **Docker support** - docker-compose.yml ready
- [x] **Examples** - Sample code for backend integration
- [ ] **Test with your backend** - Connect to your Snapchat app
- [ ] **Monitor performance** - Track API latency and success rates
- [ ] **Scale testing** - Verify under load

---

## 🤝 Integration Support

### Common Issues

**Q: "No pets detected" error even though there's a pet in the image**
- A: Ensure the image URL is publicly accessible
- A: Try a clearer image with the pet as the main subject
- A: Check YOLO model loaded correctly: `docker logs pet-roast-api`

**Q: How do I handle videos vs images?**
- A: Currently supports images only. For videos, extract a frame first and send the image URL.

**Q: Can I customize which animals are considered "pets"?**
- A: Yes! Edit `app/services/pet_detection.py` and modify `PET_CLASSES` dictionary.

**Q: How do I integrate webhooks?**
- A: See webhook examples in `BACKEND_INTEGRATION.md` and `examples/backend_client.py`

---

## 📞 Next Steps

1. **Start the services**: `docker-compose up -d`
2. **Test endpoints**: Use curl or Postman
3. **Read integration guide**: `BACKEND_INTEGRATION.md`
4. **Use client library**: `examples/backend_client.py`
5. **Connect your backend**: Follow integration patterns
6. **Monitor logs**: `docker logs -f pet-roast-api`
7. **Deploy to production**: Use Kubernetes or cloud services

---

## 🎉 You're Ready!

Your Pet Roast AI is now **production-ready** and can be integrated with your Snapchat-like backend! 🚀

For detailed API documentation, see **[BACKEND_INTEGRATION.md](./BACKEND_INTEGRATION.md)**.

---

**Made with ❤️ for the pet-loving community**
