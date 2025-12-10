# 🚂 Railway Deployment Guide for Pet Roast AI

## Quick Deploy to Railway

### 1. Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected
- Revid.ai API key

### 2. Deploy Steps

#### Option A: Deploy from GitHub
```bash
# 1. Push your code to GitHub
git add .
git commit -m "Prepare for Railway deployment"
git push origin main

# 2. Go to Railway Dashboard
# 3. Click "New Project" → "Deploy from GitHub repo"
# 4. Select your repository
# 5. Railway will auto-detect Dockerfile and deploy
```

#### Option B: Deploy with Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Environment Variables

In Railway Dashboard → Your Project → Variables, add:

```env
REVID_API_KEY=your_revid_api_key
BACKEND_WEBHOOK_URL=https://your-backend.railway.app/webhooks/pet-roast-complete
CORS_ORIGINS=["https://your-backend.railway.app"]
REDIS_URL=redis://default:password@redis.railway.internal:6379
USE_REDIS=true
```

### 4. Add Redis (Optional but Recommended)

1. In Railway Dashboard, click "+ New"
2. Select "Database" → "Add Redis"
3. Railway will automatically set `REDIS_URL` environment variable

### 5. Get Your AI Service URL

After deployment, Railway will give you a URL like:
```
https://your-ai-service.up.railway.app
```

### 6. Update Backend Configuration

In your Railway backend, set:
```env
PET_ROAST_API_URL=https://your-ai-service.up.railway.app
```

## API Endpoints

Your AI service will expose these endpoints:

### Health Check
```
GET https://your-ai-service.up.railway.app/healthz
```

### Generate Video
```
POST https://your-ai-service.up.railway.app/api/generate-video
Content-Type: application/json

{
  "text": "Roast my dog!",
  "image_url": "https://example.com/dog.jpg"
}
```

### Check Video Status
```
GET https://your-ai-service.up.railway.app/api/video-status/{job_id}
```

### Webhook (Called by Revid when video is ready)
```
POST https://your-ai-service.up.railway.app/api/webhook/video-complete
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Mobile App (Your Frontend)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ GraphQL
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         Backend (Railway) - Port 4000                        │
│         https://your-backend.railway.app                     │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API
                 ▼
┌─────────────────────────────────────────────────────────────┐
│       Pet Roast AI (Railway) - Port 8000                     │
│       https://your-ai-service.up.railway.app                 │
│                                                              │
│  • Pet Detection (YOLOv5)                                    │
│  • Translation (AI4Bharat)                                   │
│  • Video Generation (Revid.ai)                               │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─→ Redis (Railway Redis addon)
       └─→ Revid.ai (External API)
```

## Monitoring

### View Logs
```bash
railway logs
```

### Check Deployment Status
```bash
railway status
```

## Troubleshooting

### Issue: Build Fails
**Solution:** Check Dockerfile is present and valid
```bash
docker build -t test .  # Test locally first
```

### Issue: Service Won't Start
**Solution:** Check environment variables are set
```bash
railway variables  # List all variables
```

### Issue: Redis Connection Failed
**Solution:** Add Redis addon in Railway dashboard

### Issue: Backend Can't Connect
**Solution:**
1. Check BACKEND_WEBHOOK_URL is set correctly
2. Verify CORS_ORIGINS includes your backend URL
3. Check backend has correct PET_ROAST_API_URL

## Production Checklist

- [ ] Set REVID_API_KEY
- [ ] Set BACKEND_WEBHOOK_URL to your backend
- [ ] Configure CORS_ORIGINS with exact URLs
- [ ] Add Redis addon for persistence
- [ ] Set up custom domain (optional)
- [ ] Configure health check monitoring
- [ ] Set up logging/alerting
- [ ] Test all endpoints

## Cost Optimization

Railway offers:
- $5 free credit per month
- Pay only for usage beyond free tier
- Auto-scale based on traffic

For production:
- Enable autoscaling
- Set resource limits
- Monitor usage in dashboard

## Support

For Railway-specific issues:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway

For AI service issues:
- Check logs: `railway logs`
- Review this repository's documentation
