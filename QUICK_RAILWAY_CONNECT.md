# 🚀 Quick Railway Remote Connection

## One-Command Setup

```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
./setup_railway_remote.sh
```

## Manual Steps (If Script Doesn't Work)

### 1. Install Railway CLI
```bash
npm i -g @railway/cli
```

### 2. Login
```bash
railway login
```
(Opens browser - authenticate there)

### 3. Connect to Project
```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
railway link d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
```

### 4. Set Variables
```bash
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
railway variables set FAL_BASE_URL="https://queue.fal.run"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video"
railway variables set USE_REDIS="true"
railway variables set VIDEO_STORAGE_PATH="storage/videos"
```

### 5. Verify
```bash
railway status
railway logs --tail 20
```

## ✅ You're Connected!

Now you can manage Railway remotely:
- `railway logs --follow` - Watch logs
- `railway status` - Check status  
- `railway up` - Deploy
- `railway variables` - View variables
