# 🚂 Railway Project Information

## Project Details

- **Project Name**: `pet_roasting`
- **Project ID**: `d3e9f8f4-cdca-4825-9ec4-f7fa9844d266`
- **Environment ID**: `d07ed2df-e646-45dd-9510-b40b1ceee70d`
- **Project URL**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

## 🔗 Quick Links

### Dashboard
- **Main Dashboard**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
- **Environment**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266?environmentId=d07ed2df-e646-45dd-9510-b40b1ceee70d

### Key Sections
- **Deployments**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/deployments
- **Variables**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/variables
- **Logs**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/logs
- **Settings**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/settings
- **Networking**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/settings/networking

## 📋 Required Environment Variables

Add these in Railway Dashboard → Variables:

```bash
# Required - fal.ai Configuration
FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a
FAL_BASE_URL=https://queue.fal.run
FAL_MODEL_ID=fal-ai/minimax-video

# Optional but Recommended
USE_REDIS=true
VIDEO_STORAGE_PATH=storage/videos
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5

# CORS Configuration
CORS_ORIGINS=["*"]
```

## 🔧 Railway CLI Commands

If you have Railway CLI installed:

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

# View project status
railway status

# View environment variables
railway variables

# View logs
railway logs

# Open in browser
railway open

# Deploy
railway up
```

## 🔍 Diagnostic Checklist

### 1. Check Deployment Status
- [ ] Go to Deployments tab
- [ ] Check latest deployment status
- [ ] Review build logs for errors
- [ ] Ensure build completes successfully

### 2. Check Environment Variables
- [ ] Go to Variables tab
- [ ] Verify `FAL_API_KEY` is set
- [ ] Verify `FAL_BASE_URL=https://queue.fal.run`
- [ ] Verify `FAL_MODEL_ID=fal-ai/minimax-video`
- [ ] Check all required variables are present

### 3. Check Runtime Logs
- [ ] Go to Logs tab
- [ ] Look for "Application startup complete"
- [ ] Check for ERROR or WARNING messages
- [ ] Verify Redis connection (if enabled)
- [ ] Verify video storage initialization

### 4. Test Application
- [ ] Get public URL from Settings → Networking
- [ ] Test health endpoint: `GET /healthz`
- [ ] Test API docs: `GET /docs`
- [ ] Test video generation: `POST /api/generate-video`

## 🚨 Common Issues & Solutions

### Issue: Build Fails
**Solution**: 
- Check build logs in Deployments tab
- Verify Dockerfile is correct
- Ensure all dependencies in requirements.txt

### Issue: App Crashes on Startup
**Solution**:
- Check runtime logs
- Verify `FAL_API_KEY` is set correctly
- Check for missing environment variables

### Issue: Health Check Fails
**Solution**:
- Verify app is running (check logs)
- Check PORT is set correctly
- Verify networking settings

### Issue: Video Generation Not Working
**Solution**:
- Verify `FAL_API_KEY` is correct
- Check `FAL_BASE_URL=https://queue.fal.run`
- Check `FAL_MODEL_ID=fal-ai/minimax-video`
- Review logs for fal.ai API errors

## 📊 Monitoring

### Health Check
Once deployed, test your health endpoint:
```bash
curl https://your-app.railway.app/healthz
```
Expected: `{"status":"ok"}`

### API Documentation
Visit: `https://your-app.railway.app/docs`

### Logs
Monitor logs in real-time:
- Railway Dashboard → Logs tab
- Or use: `railway logs` (if CLI installed)

## 🔐 Security Notes

1. **Never commit API keys** to GitHub
2. Use Railway Variables for sensitive data
3. Set `CORS_ORIGINS` to specific domains in production
4. Consider adding authentication for production

## 📞 Support

- **Railway Docs**: https://docs.railway.app
- **Railway Support**: support@railway.app
- **GitHub Issues**: https://github.com/Chetupatil24/GEN_AI/issues

---

**Last Updated**: After Railway project setup
**Project**: pet_roasting
**Project ID**: d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
