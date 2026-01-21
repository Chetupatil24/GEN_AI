# 🔑 Get Full Railway Token

## The Issue

The token shown in Railway UI is **partially hidden** (`****-d002`). We need the **FULL token** that was shown when you first created it.

## Solution: Get Full Token

### Option 1: Create New Token (Recommended)

1. Go to: https://railway.app/account/tokens
2. Click **"New Token"** button
3. Give it a name: `CLI Access` or `Cursor CLI`
4. **IMPORTANT**: Copy the FULL token immediately (it shows only once!)
5. The token will look like: `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` or similar
6. Use it in the script

### Option 2: Check if Token is Saved

If you saved the token when you created it, check:
- Your password manager
- Notes/documentation
- Terminal history (if you used it before)

### Option 3: Use Railway Dashboard (Easiest - No Token Needed!)

Since token authentication is tricky, use the web dashboard:

1. **Open**: https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266
2. **Go to Variables tab**
3. **Add these variables**:

```
FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a
FAL_BASE_URL=https://queue.fal.run
FAL_MODEL_ID=fal-ai/minimax-video
USE_REDIS=true
VIDEO_STORAGE_PATH=storage/videos
```

4. **Save** - Railway auto-deploys

## Using the Full Token

Once you have the FULL token:

```bash
cd /home/chetan-patil/myprojects/1/GEN_AI
export RAILWAY_TOKEN="your-full-token-here"
./connect_and_fix_all.sh
```

Or update the script with your token:

```bash
# Edit connect_and_fix_all.sh
# Replace: export RAILWAY_TOKEN="d2438d39-dad1-4761-a423-bf02d3bdd002"
# With: export RAILWAY_TOKEN="your-full-token-here"
```

## ✅ Recommended: Use Dashboard

The easiest way is to use Railway Dashboard - no token needed!

Just set the variables in the web interface and Railway handles everything.
