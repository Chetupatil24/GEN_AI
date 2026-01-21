# 🔑 Railway Token Authentication Guide

## Getting Your Railway Token

The token you provided might need to be obtained from Railway Dashboard.

### Method 1: Get Token from Railway Dashboard

1. Go to: https://railway.app/account/tokens
2. Click **"Create Token"**
3. Give it a name (e.g., "CLI Access")
4. Copy the token (it will be longer, like: `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
5. Use it as shown below

### Method 2: Use Railway Login (Recommended)

Instead of using a token, use interactive login:

```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
railway login
```

This opens your browser and completes authentication automatically.

## Using the Token

Once you have the correct token:

```bash
export RAILWAY_TOKEN="your-token-here"
railway whoami  # Verify it works
```

## Alternative: Use Railway Dashboard Directly

If token authentication doesn't work, use the web dashboard:

1. **Go to your project**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

2. **Set Variables** (Variables tab):
   - `FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a`
   - `FAL_BASE_URL=https://queue.fal.run`
   - `FAL_MODEL_ID=fal-ai/minimax-video`
   - `USE_REDIS=true`
   - `VIDEO_STORAGE_PATH=storage/videos`

3. **Check Deployment** (Deployments tab)

4. **View Logs** (Logs tab)

## ✅ Recommended: Use Railway Login

The easiest way is:

```bash
railway login
./fix_all_railway.sh
```

This handles everything automatically!
