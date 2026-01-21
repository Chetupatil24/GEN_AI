# 🔧 Railway Fix All Guide

Complete step-by-step guide to connect to Railway and fix all deployment issues.

## 🚀 Quick Fix (Automated)

### Option 1: Use Railway CLI Script

```bash
# Run the automated fix script
./railway_fix_all.sh
```

This script will:
- ✅ Check Railway CLI installation
- ✅ Login to Railway
- ✅ Link to your project
- ✅ Check and set all required environment variables
- ✅ Show deployment status and logs

### Option 2: Manual Fix via Dashboard

1. **Go to Railway Dashboard:**
   ```
   https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
   ```

2. **Check Variables Tab:**
   - Go to: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/variables
   - Add/verify these variables:

## 📋 Required Environment Variables

### Critical Variables (Must Have)

```bash
FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a
FAL_BASE_URL=https://queue.fal.run
FAL_MODEL_ID=fal-ai/minimax-video
```

### Recommended Variables

```bash
USE_REDIS=true
VIDEO_STORAGE_PATH=storage/videos
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
CORS_ORIGINS=["*"]
```

## 🔍 Step-by-Step Fix Process

### Step 1: Install Railway CLI (if not installed)

```bash
npm i -g @railway/cli
```

### Step 2: Login to Railway

```bash
railway login
```

This will open your browser for authentication.

### Step 3: Link to Project

```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
```

### Step 4: Check Current Variables

```bash
railway variables
```

### Step 5: Set Missing Variables

```bash
# Required variables
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
railway variables set FAL_BASE_URL="https://queue.fal.run"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video"

# Optional but recommended
railway variables set USE_REDIS="true"
railway variables set VIDEO_STORAGE_PATH="storage/videos"
railway variables set REQUEST_TIMEOUT_SECONDS="30.0"
railway variables set MAX_RETRIES="3"
railway variables set RETRY_BACKOFF_FACTOR="1.5"
```

### Step 6: Check Deployment Status

```bash
railway status
```

### Step 7: View Logs

```bash
# View live logs
railway logs

# View last 50 lines
railway logs --tail 50
```

### Step 8: Redeploy (if needed)

```bash
railway up
```

Or trigger redeploy from Railway Dashboard → Deployments → Redeploy

## 🔍 Diagnostic Commands

### Check Project Info

```bash
railway status
railway whoami
```

### View All Variables

```bash
railway variables
```

### Get Specific Variable

```bash
railway variables get FAL_API_KEY
```

### View Recent Logs

```bash
railway logs --tail 100
```

### Open in Browser

```bash
railway open
```

## 🚨 Common Issues & Fixes

### Issue 1: Railway CLI Not Installed

**Fix:**
```bash
npm i -g @railway/cli
```

### Issue 2: Not Logged In

**Fix:**
```bash
railway login
```

### Issue 3: Project Not Linked

**Fix:**
```bash
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
```

### Issue 4: Variables Not Set

**Fix:**
Use the script `./railway_fix_all.sh` or set manually via dashboard or CLI.

### Issue 5: Build Fails

**Check:**
1. Go to Railway Dashboard → Deployments
2. Click on latest deployment
3. Review build logs
4. Check for missing dependencies or errors

**Fix:**
- Ensure all files are committed and pushed to GitHub
- Check Dockerfile is correct
- Verify requirements.txt has all dependencies

### Issue 6: App Crashes on Startup

**Check:**
```bash
railway logs
```

Look for:
- Missing environment variables
- Import errors
- Connection errors

**Fix:**
- Set all required environment variables
- Check logs for specific error messages
- Verify FAL_API_KEY is correct

### Issue 7: Health Check Fails

**Test:**
```bash
# Get your Railway URL
railway open

# Then test
curl https://your-app.railway.app/healthz
```

**Fix:**
- Check app is running (railway logs)
- Verify PORT is set correctly
- Check networking settings in Railway Dashboard

## 📊 Verification Checklist

After running fixes, verify:

- [ ] Railway CLI installed and logged in
- [ ] Project linked correctly
- [ ] All required environment variables set
- [ ] Latest code pushed to GitHub
- [ ] Deployment successful (check Railway Dashboard)
- [ ] Application starts without errors (check logs)
- [ ] Health endpoint responds: `{"status":"ok"}`
- [ ] API docs accessible at `/docs`

## 🎯 Quick Reference

### Railway Dashboard Links

- **Main**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
- **Variables**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/variables
- **Logs**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/logs
- **Deployments**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266/deployments

### Useful Commands

```bash
# Quick status check
railway status

# View logs
railway logs

# Set variable
railway variables set KEY="value"

# Open dashboard
railway open

# Redeploy
railway up
```

## ✅ Success Indicators

You'll know everything is fixed when:

1. ✅ `railway status` shows project is active
2. ✅ All required variables are set
3. ✅ `railway logs` shows "Application startup complete"
4. ✅ Health endpoint returns `{"status":"ok"}`
5. ✅ No ERROR messages in logs
6. ✅ Video generation works end-to-end

---

**Run `./railway_fix_all.sh` for automated fix!**
