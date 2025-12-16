# 🧪 Postman Testing Guide - Pet Roast AI Service

Complete guide for testing all endpoints with Postman.

---

## 📥 Import Postman Collection

1. **Open Postman**
2. **Click "Import"** (top left)
3. **Select** `postman_collection.json` from this directory
4. **Collection imported!** You'll see "Pet Roast AI Service" in your collections

---

## ⚙️ Configure Environment Variables

### Step 1: Create Environment

1. Click "Environments" (left sidebar)
2. Click "+" to create new environment
3. Name it: "Pet Roast Local" or "Pet Roast Railway"

### Step 2: Set Variables

| Variable | Value (Local) | Value (Railway) |
|----------|---------------|-----------------|
| `base_url` | `http://localhost:8000` | `https://your-service.railway.app` |
| `backend_url` | `http://localhost:3000` | `https://your-backend.railway.app` |
| `job_id` | *(auto-set)* | *(auto-set)* |

### Step 3: Activate Environment

1. Select your environment from dropdown (top right)
2. Click the eye icon to view/edit variables

---

## 🚀 Testing Workflow

### Test 1: Health Check ✅

**Endpoint:** `GET /healthz`

**Expected Response (200):**
```json
{
  "status": "ok"
}
```

**What it tests:**
- ✅ Service is running
- ✅ FastAPI is responding

**Troubleshooting:**
- If fails: Check service is running with `uvicorn app.main:app --reload`

---

### Test 2: Backend Connection Test ✅

**Endpoint:** `GET /api/test-backend-connection`

**Expected Response (200) - If configured:**
```json
{
  "status": "success",
  "message": "Backend is reachable",
  "backend_url": "https://your-backend.railway.app/webhooks/pet-roast-complete",
  "response_code": 200,
  "response_time_ms": 145.23
}
```

**Expected Response (200) - If not configured:**
```json
{
  "status": "not_configured",
  "message": "BACKEND_WEBHOOK_URL environment variable not set",
  "backend_url": null
}
```

**What it tests:**
- ✅ Backend webhook URL configured
- ✅ Backend is reachable
- ✅ Network connectivity

---

### Test 3: Generate Video (with Pet Detection) 🎬

**Endpoint:** `POST /api/generate-video`

**Request Body:**
```json
{
  "text": "Roast my adorable lazy pet!",
  "image_url": "https://images.unsplash.com/photo-1543466835-00a7907e9de1"
}
```

**Expected Response (202 Accepted):**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "queued"
}
```

**What it tests:**
- ✅ Pet detection (YOLOv5)
- ✅ AI4Bharat translation
- ✅ Revid.ai video job creation
- ✅ Redis job storage

**Notes:**
- ✅ The `job_id` is automatically saved to collection variables
- ✅ Use a **dog or cat image** for testing
- ⏱️ Processing takes 30-90 seconds

**Test Images:**
```
✅ Dog: https://images.unsplash.com/photo-1543466835-00a7907e9de1
✅ Cat: https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba
✅ Bird: https://images.unsplash.com/photo-1552728089-57bdde30beb3
```

---

### Test 4: Check Video Status 🔍

**Endpoint:** `GET /api/video-status/{{job_id}}`

**Expected Response (200) - Processing:**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "processing",
  "detail": null,
  "updated_at": "2025-12-16T10:00:00Z"
}
```

**Expected Response (200) - Completed:**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "completed",
  "detail": null,
  "updated_at": "2025-12-16T10:05:00Z",
  "video_url": "https://revid.ai/videos/abc123.mp4"
}
```

**What it tests:**
- ✅ Job status retrieval
- ✅ Redis persistence
- ✅ Revid.ai status polling

**Status Progression:**
1. `queued` - Job created
2. `processing` - Video being generated
3. `completed` - Video ready (includes video_url)
4. `failed` - Generation failed (includes error detail)

**Polling Tip:**
- Poll every **5 seconds**
- Typically completes in **30-90 seconds**
- Use Postman "Runner" for automated polling

---

### Test 5: Translate Text (AI4Bharat) 🌍

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

**Expected Response (200):**
```json
{
  "translated_text": "Roast my dog",
  "source_language": "hi",
  "target_language": "en",
  "task": "translation",
  "provider_metadata": {}
}
```

**What it tests:**
- ✅ AI4Bharat/IndicTrans2 integration
- ✅ Hindi to English translation
- ✅ Translation endpoint standalone

**Supported Languages:**
- Hindi (hi), Bengali (bn), Gujarati (gu), Marathi (mr)
- Kannada (kn), Telugu (te), Malayalam (ml), Tamil (ta)
- Punjabi (pa), Odia (or), Assamese (as), Urdu (ur)

---

### Test 6: Webhook - Video Complete (Simulated) 🔔

**Endpoint:** `POST /api/webhook/video-complete`

**Request Headers:**
```
Content-Type: application/json
X-Webhook-Source: revid-ai
```

**Request Body:**
```json
{
  "job_id": "{{job_id}}",
  "status": "completed",
  "video_url": "https://example.com/test-video.mp4"
}
```

**Expected Response (200):**
```json
{
  "status": "success",
  "message": "Webhook processed for job rev_abc123xyz",
  "job_id": "rev_abc123xyz"
}
```

**What it tests:**
- ✅ Webhook endpoint
- ✅ Job status update
- ✅ Backend notification (if configured)
- ✅ Retry logic

**Check Logs:**
```bash
# You should see in terminal:
📥 Webhook received for job rev_abc123xyz: status=completed
✅ Updated job rev_abc123xyz in store: completed
🔔 Notifying backend at https://your-backend.railway.app/...
✅ Backend notified successfully (attempt 1/3)
```

---

### Test 7: No Pets Detection (Error Test) ❌

**Endpoint:** `POST /api/generate-video`

**Request Body:**
```json
{
  "text": "Test with no pets",
  "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": {
    "error": "no_pets_detected",
    "message": "No pets found in the uploaded image. Please upload an image or video containing pets (dogs, cats, birds, etc.) to generate a roast video.",
    "suggestion": "Try uploading a clear photo or video of your pet."
  }
}
```

**What it tests:**
- ✅ Pet detection validation
- ✅ User-friendly error messages
- ✅ Error handling

---

### Test 8: Get Video Result 📹

**Endpoint:** `GET /api/video-result/{{job_id}}`

**Expected Response (200) - Completed:**
```json
{
  "job_id": "rev_abc123xyz",
  "status": "completed",
  "video_url": "https://revid.ai/videos/abc123.mp4",
  "detail": null
}
```

**Expected Response (409 Conflict) - Still Processing:**
```json
{
  "detail": "Video generation still in progress."
}
```

**What it tests:**
- ✅ Final video URL retrieval
- ✅ Completion verification

---

## 🔄 Complete Testing Workflow

### Quick Test (5 minutes)

```
1. Health Check                   → ✅ Service running
2. Test Backend Connection        → ✅ Backend configured
3. Generate Video (pet image)     → ✅ Get job_id
4. Wait 30 seconds
5. Check Video Status             → ✅ Should be "processing"
6. Wait 60 seconds
7. Check Video Status again       → ✅ Should be "completed"
8. Get Video Result               → ✅ Get video_url
```

### Complete Test (10 minutes)

```
1. Health Check                   → ✅
2. Test Backend Connection        → ✅
3. Translate Text                 → ✅ Test AI4Bharat
4. Generate Video (pet image)     → ✅ Save job_id
5. No Pets Test                   → ❌ Expected error
6. Check Video Status (poll)      → ✅ Track progress
7. Simulate Webhook               → ✅ Test webhook
8. Get Video Result               → ✅ Final video
```

---

## 📊 Expected Results Summary

| Test | Expected Status | Expected Time |
|------|----------------|---------------|
| Health Check | 200 OK | <100ms |
| Backend Connection | 200 OK | ~150ms |
| Generate Video | 202 Accepted | ~2-5s |
| Video Status (initial) | 200 OK (queued) | <500ms |
| Video Status (final) | 200 OK (completed) | 30-90s |
| Translate Text | 200 OK | ~1-3s |
| Webhook | 200 OK | <1s |
| No Pets Error | 400 Bad Request | ~2-3s |

---

## 🐛 Troubleshooting

### Issue: Health check fails
**Solution:**
```bash
# Start the service
uvicorn app.main:app --reload --port 8000

# Check it's running
curl http://localhost:8000/healthz
```

### Issue: Backend connection test returns "not_configured"
**Solution:**
```bash
# Set environment variable
export BACKEND_WEBHOOK_URL="https://your-backend.railway.app/webhooks/pet-roast-complete"

# Or add to .env file
echo 'BACKEND_WEBHOOK_URL=https://your-backend.railway.app/webhooks/pet-roast-complete' >> .env
```

### Issue: Generate video returns 400 "No pets detected"
**Solution:**
- Use a clear pet image (dog, cat, bird, etc.)
- Try test images provided above
- Check image URL is publicly accessible

### Issue: Video status stays "processing" forever
**Solution:**
- Check Revid.ai API key is valid
- Check Revid.ai account has credits
- View logs for errors: Check terminal output

### Issue: Webhook not received by backend
**Solution:**
```bash
# Check backend URL is correct
curl -X POST https://your-backend.railway.app/webhooks/pet-roast-complete \
  -H "Content-Type: application/json" \
  -d '{"job_id":"test","status":"completed"}'

# Check logs for webhook attempts
# Look for: "🔔 Notifying backend at..."
```

---

## 🎯 Postman Runner (Automated Testing)

### Setup Runner

1. **Click "Runner"** (bottom right in Postman)
2. **Select collection:** "Pet Roast AI Service"
3. **Select environment:** Your environment
4. **Set iterations:** 1
5. **Set delay:** 5000ms (5 seconds between requests)

### Test Sequence

```
✅ Health Check
✅ Backend Connection Test
✅ Generate Video
⏸️  (wait 30s)
✅ Check Video Status
⏸️  (wait 30s)
✅ Check Video Status
⏸️  (wait 30s)
✅ Get Video Result
```

### Automated Test Script

Add to **Tests** tab in Postman:

```javascript
// For Generate Video request
pm.test("Status code is 202", function () {
    pm.response.to.have.status(202);
});

pm.test("Response has job_id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('job_id');
    pm.collectionVariables.set('job_id', jsonData.job_id);
});

// For Video Status request
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has status field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
});
```

---

## 📝 Environment Setup Examples

### Local Development
```json
{
  "base_url": "http://localhost:8000",
  "backend_url": "http://localhost:3000",
  "job_id": ""
}
```

### Railway Staging
```json
{
  "base_url": "https://staging-ai-service.up.railway.app",
  "backend_url": "https://staging-backend.railway.app",
  "job_id": ""
}
```

### Railway Production
```json
{
  "base_url": "https://ai-service.up.railway.app",
  "backend_url": "https://backend.railway.app",
  "job_id": ""
}
```

---

## ✅ Verification Checklist

After running all tests, verify:

- [ ] ✅ Health check returns 200
- [ ] ✅ Backend connection test succeeds
- [ ] ✅ Can generate video with pet image
- [ ] ✅ Receives job_id in response
- [ ] ✅ Can check video status
- [ ] ✅ Status progresses: queued → processing → completed
- [ ] ✅ Receives video_url when completed
- [ ] ✅ Translation works (if AI4Bharat configured)
- [ ] ✅ Webhook endpoint accepts callbacks
- [ ] ✅ No pets error returns 400
- [ ] ✅ Backend receives webhook (if configured)

---

## 🎉 Success Criteria

Your API is working perfectly when:

✅ All health checks pass
✅ Pet detection validates images correctly
✅ Videos generate within 90 seconds
✅ Webhooks deliver to backend reliably
✅ Error messages are user-friendly
✅ Status tracking works accurately

---

**Need help?** Check the logs in your terminal or review [API_REFERENCE.md](API_REFERENCE.md) for detailed documentation.

---

**Last Updated:** December 16, 2025
**Version:** 1.0.0
