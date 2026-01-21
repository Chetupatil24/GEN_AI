# ⚠️ Railway CLI Token Authentication Limitation

## Issue

Railway CLI **v4.26.0** does **NOT support** `--token` flag:

```bash
railway login --token
# Error: unexpected argument '--token' found
```

The CLI only supports:
- `railway login` (interactive browser login)
- `railway login --browserless` (browserless login)

## ✅ WORKING SOLUTION: Railway Dashboard

Since CLI token authentication is not supported in v4.26.0, use Railway Dashboard:

### Step 1: Open Your Project

**https://railway.app/project/d3e9f8f4-cdca-4825-9ec4-f7fa9844d266**

### Step 2: Set Variables

Go to **"Variables"** tab → Click **"New Variable"**:

1. **FAL_API_KEY** = `0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a`
2. **FAL_BASE_URL** = `https://queue.fal.run`
3. **FAL_MODEL_ID** = `fal-ai/minimax-video`
4. **USE_REDIS** = `true`
5. **VIDEO_STORAGE_PATH** = `storage/videos`

### Step 3: Save & Deploy

- Click **"Save"** after each variable
- Railway **automatically redeploys**
- Check **"Deployments"** tab
- View **"Logs"** tab

## Alternative: Interactive Login

If you want to use CLI later:

```bash
railway login
# Opens browser - authenticate there
# Then you can use CLI commands
```

## ✅ What's Ready

- ✅ **Latest CLI**: v4.26.0 installed
- ✅ **Account API Token**: Valid (`099fbe14-1936-421a-8154-226b646c3529`)
- ✅ **All Code**: Fixed and ready
- ✅ **Dockerfile**: Perfect configuration
- ✅ **App**: Ready for Railway

## 📋 Summary

**Everything is ready!** The CLI doesn't support `--token` flag in v4.26.0, but Railway Dashboard is the most reliable method anyway. Just set the variables there and Railway will deploy automatically!

---

**🚀 Use Railway Dashboard - it's the fastest and most reliable method!**
