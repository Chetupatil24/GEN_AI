# 🔧 Railway Troubleshooting Guide
## Project ID: d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

Complete troubleshooting guide for Railway deployment issues.

## 🚨 Common Issues & Fixes

### Issue 1: Build Fails - YOLO Model Download

**Symptoms:**
- Build fails during Docker build
- Error: "Failed to download YOLO model"

**Fix Applied:**
- ✅ Added error handling in Dockerfile
- Model will download at runtime if build-time download fails

**Manual Fix:**
```dockerfile
# In Dockerfile, line 21 is now:
RUN python -c "import torch; torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)" || echo "Will download at runtime"
```

### Issue 2: Application Crashes on Startup

**Symptoms:**
- App starts but immediately crashes
- Logs show: "FAL_API_KEY Field required"

**Fix:**
1. Go to Railway Dashboard → Variables
2. Add: `FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a`
3. Add: `FAL_BASE_URL=https://queue.fal.run`
4. Add: `FAL_MODEL_ID=fal-ai/minimax-video`
5. Redeploy

### Issue 3: Port Binding Error

**Symptoms:**
- Error: "Address already in use"
- App can't bind to port

**Fix Applied:**
- ✅ Using `$PORT` environment variable (Railway auto-sets this)
- ✅ Dockerfile CMD uses `${PORT:-8000}` fallback

**Verify:**
- Check Railway logs show: "Uvicorn running on http://0.0.0.0:PORT"
- PORT is automatically set by Railway

### Issue 4: Redis Connection Failed

**Symptoms:**
- Logs show: "Redis connection failed"
- Falls back to in-memory storage

**Fix:**
1. Add Redis service in Railway:
   - Dashboard → "+ New" → "Database" → "Redis"
2. Set `USE_REDIS=true` in Variables
3. `REDIS_URL` is auto-set by Railway

**Or disable Redis:**
- Set `USE_REDIS=false` in Variables
- App will use in-memory storage (not persistent)

### Issue 5: Storage Directory Permission Denied

**Symptoms:**
- Error: "Permission denied" when saving videos
- Videos not saving

**Fix Applied:**
- ✅ Storage service now handles permission errors
- ✅ Falls back to `/tmp/videos` if storage directory fails
- ✅ Dockerfile creates directory with proper permissions

### Issue 6: Video Generation Not Working

**Symptoms:**
- Status shows "completed" but no video URL
- Video URL is None

**Check:**
1. Verify `FAL_API_KEY` is correct
2. Check `FAL_BASE_URL=https://queue.fal.run`
3. Check `FAL_MODEL_ID=fal-ai/minimax-video`
4. Review Railway logs for fal.ai API errors

**Fix:**
- All environment variables must be set correctly
- Check Railway logs for detailed error messages

## 📋 Required Environment Variables

Add these in Railway Dashboard → Variables:

```bash
# Required
FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a
FAL_BASE_URL=https://queue.fal.run
FAL_MODEL_ID=fal-ai/minimax-video

# Optional but Recommended
USE_REDIS=true
VIDEO_STORAGE_PATH=storage/videos
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5

# CORS (adjust for your domain)
CORS_ORIGINS=["*"]
```

## 🔍 Diagnostic Steps

### Step 1: Check Build Logs
1. Go to Railway Dashboard
2. Click on your project
3. Go to "Deployments" tab
4. Click on latest deployment
5. Review build logs for errors

### Step 2: Check Runtime Logs
1. Go to "Logs" tab
2. Look for:
   - "Application startup complete" ✅
   - "Using Redis for persistent job storage" ✅
   - "Video storage initialized" ✅
   - Any ERROR or WARNING messages

### Step 3: Test Health Endpoint
```bash
curl https://your-app.railway.app/healthz
```
Expected: `{"status":"ok"}`

### Step 4: Test API Documentation
Visit: `https://your-app.railway.app/docs`
Should show Swagger UI

### Step 5: Test Video Generation
```bash
curl -X POST https://your-app.railway.app/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test roast",
    "image_url": "https://example.com/pet.jpg"
  }'
```

## 🛠️ Quick Fixes

### Fix 1: Redeploy with Correct Variables
1. Update all environment variables
2. Go to "Deployments" → "Redeploy"

### Fix 2: Clear Build Cache
1. Go to "Settings" → "Build"
2. Clear build cache
3. Redeploy

### Fix 3: Check Resource Limits
1. Go to "Settings" → "Resources"
2. Ensure sufficient memory/CPU allocated
3. YOLO model needs ~2GB RAM

### Fix 4: Enable Debug Logging
Add to Variables:
```bash
LOG_LEVEL=DEBUG
```

## 📞 Get Help

1. **Railway Logs**: Check logs tab for detailed errors
2. **GitHub Issues**: https://github.com/Chetupatil24/GEN_AI/issues
3. **Railway Support**: support@railway.app

## ✅ Verification Checklist

- [ ] All required environment variables set
- [ ] Build completes successfully
- [ ] Application starts without errors
- [ ] Health endpoint returns `{"status":"ok"}`
- [ ] API docs accessible at `/docs`
- [ ] Video generation endpoint works
- [ ] Redis connected (if enabled)
- [ ] Storage directory created

---

**Last Updated**: After fixing Railway deployment issues
**Project ID**: d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
