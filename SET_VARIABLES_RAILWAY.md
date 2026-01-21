# 🔧 Set Variables on Railway Dashboard

Since token authentication needs the correct format, here's how to set variables via Railway Dashboard:

## Quick Steps

1. **Open Railway Dashboard**:
   https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

2. **Go to Variables Tab**

3. **Add These Variables**:

```
FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a
FAL_BASE_URL=https://queue.fal.run
FAL_MODEL_ID=fal-ai/minimax-video
USE_REDIS=true
VIDEO_STORAGE_PATH=storage/videos
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
```

4. **Save** - Railway will automatically redeploy

5. **Check Deployments Tab** - Monitor build status

6. **View Logs Tab** - Check for any errors

## ✅ After Setting Variables

Your deployment should automatically:
- ✅ Build with all dependencies
- ✅ Start with correct configuration
- ✅ Be ready to generate videos

## 🎯 Test Your Deployment

Once deployed, test the health endpoint:

```bash
# Get your Railway URL from dashboard
curl https://your-app.railway.app/healthz
```

Expected: `{"status":"ok"}`

## 📋 All Variables Explained

- **FAL_API_KEY**: Your fal.ai API key for video generation
- **FAL_BASE_URL**: fal.ai API endpoint
- **FAL_MODEL_ID**: Model to use for video generation
- **USE_REDIS**: Enable Redis for job persistence
- **VIDEO_STORAGE_PATH**: Where to store generated videos
- **REQUEST_TIMEOUT_SECONDS**: API request timeout
- **MAX_RETRIES**: Maximum retry attempts
- **RETRY_BACKOFF_FACTOR**: Retry backoff multiplier

---

**✅ Set these variables in Railway Dashboard and your app will be ready!**
