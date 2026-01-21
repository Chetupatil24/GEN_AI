#!/bin/bash
# Final Railway Connection and Fix All - Using Token

export RAILWAY_TOKEN="d2438d39-dad1-4761-a423-bf02d3bdd002"
PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Railway Connection & Fix All (Final)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Verify authentication
echo "Step 1: Verifying authentication..."
if railway whoami &> /dev/null 2>&1; then
    echo "✅ Authenticated successfully"
    railway whoami
else
    echo "❌ Authentication failed"
    echo "⚠️  Token might be invalid or need different format"
    exit 1
fi

# Step 2: Link to project
echo ""
echo "Step 2: Linking to project..."
railway link --project "$PROJECT_ID" 2>/dev/null && echo "✅ Linked" || echo "⚠️  Already linked"

# Step 3: Set all variables
echo ""
echo "Step 3: Setting environment variables..."
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a" && echo "✅ FAL_API_KEY"
railway variables set FAL_BASE_URL="https://queue.fal.run" && echo "✅ FAL_BASE_URL"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video" && echo "✅ FAL_MODEL_ID"
railway variables set USE_REDIS="true" && echo "✅ USE_REDIS"
railway variables set VIDEO_STORAGE_PATH="storage/videos" && echo "✅ VIDEO_STORAGE_PATH"

# Step 4: Verify
echo ""
echo "Step 4: Deployment status..."
railway status 2>&1

echo ""
echo "Step 5: Recent logs..."
railway logs --tail 15 2>&1 | head -30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Commands:"
echo "  railway logs --follow    # Watch logs"
echo "  railway status           # Check status"
echo "  railway up               # Deploy"
echo ""
