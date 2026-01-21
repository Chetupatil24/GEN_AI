# 🔌 Final Railway Connection Steps

## ✅ What's Done
- ✅ Railway CLI installed
- ✅ All scripts created
- ✅ Code pushed to GitHub

## 🚀 Connect Now (3 Steps)

### Step 1: Login to Railway
```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
railway login
```
**This will open your browser - authenticate there!**

### Step 2: After Login, Run Connection Script
```bash
./connect_now.sh
```

### Step 3: Verify Connection
```bash
railway status
railway logs --tail 20
```

## 📋 Complete Manual Steps

If you prefer to do everything manually:

```bash
# 1. Login
railway login

# 2. Link to project
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

# 3. Set all variables
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
railway variables set FAL_BASE_URL="https://queue.fal.run"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video"
railway variables set USE_REDIS="true"
railway variables set VIDEO_STORAGE_PATH="storage/videos"

# 4. Verify
railway status
railway variables
railway logs --tail 50
```

## ✅ After Connection

You can now manage Railway remotely:

```bash
# Watch logs in real-time
railway logs --follow

# Check status
railway status

# View variables
railway variables

# Deploy
railway up

# Open dashboard
railway open
```

## 🎯 Quick Test

After connecting, test your deployment:

```bash
# Get your Railway URL
railway open

# Then test health endpoint
curl https://your-app.railway.app/healthz
```

Expected: `{"status":"ok"}`
