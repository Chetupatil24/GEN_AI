#!/bin/bash
# Quick Railway Connection Script

PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"

echo "🔌 Connecting to Railway..."
echo ""

# Check if logged in
if railway whoami &> /dev/null; then
    echo "✅ Already logged in"
    railway whoami
else
    echo "🔐 Logging in to Railway..."
    echo "⚠️  Browser will open - please authenticate"
    railway login
fi

echo ""
echo "🔗 Linking to project..."
railway link "$PROJECT_ID" 2>/dev/null || echo "✅ Already linked"

echo ""
echo "📋 Setting environment variables..."
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a" 2>/dev/null && echo "✅ FAL_API_KEY" || echo "⚠️  FAL_API_KEY"
railway variables set FAL_BASE_URL="https://queue.fal.run" 2>/dev/null && echo "✅ FAL_BASE_URL" || echo "⚠️  FAL_BASE_URL"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video" 2>/dev/null && echo "✅ FAL_MODEL_ID" || echo "⚠️  FAL_MODEL_ID"
railway variables set USE_REDIS="true" 2>/dev/null && echo "✅ USE_REDIS" || echo "⚠️  USE_REDIS"
railway variables set VIDEO_STORAGE_PATH="storage/videos" 2>/dev/null && echo "✅ VIDEO_STORAGE_PATH" || echo "⚠️  VIDEO_STORAGE_PATH"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Connected to Railway!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Project Status:"
railway status
echo ""
echo "📋 View logs: railway logs --follow"
echo "🚀 Deploy: railway up"
echo "🌐 Open dashboard: railway open"
echo ""
