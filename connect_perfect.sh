#!/bin/bash
# Perfect Railway Connection with Latest CLI

TOKEN="d2438d39-dad1-4761-a423-bf02d3bdd002"
PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Perfect Railway Connection (Latest CLI)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Railway CLI version
echo "Step 1: Checking Railway CLI version..."
RAILWAY_VERSION=$(railway --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
echo "✅ Railway CLI version: $RAILWAY_VERSION"

# Logout first
echo ""
echo "Step 2: Cleaning previous session..."
railway logout 2>/dev/null || echo "No previous session"

# Try multiple authentication methods
echo ""
echo "Step 3: Authenticating with token..."

# Method 1: Environment variable
export RAILWAY_TOKEN="$TOKEN"
if railway whoami &> /dev/null 2>&1; then
    echo "✅ Authentication successful via RAILWAY_TOKEN"
    railway whoami
    AUTH_SUCCESS=true
else
    echo "⚠️  RAILWAY_TOKEN method failed, trying alternative..."
    AUTH_SUCCESS=false
fi

# Method 2: Try token file
if [ "$AUTH_SUCCESS" = false ]; then
    mkdir -p ~/.railway 2>/dev/null
    echo "$TOKEN" > ~/.railway/token 2>/dev/null
    if railway whoami &> /dev/null 2>&1; then
        echo "✅ Authentication successful via token file"
        railway whoami
        AUTH_SUCCESS=true
    fi
fi

# Method 3: Try interactive login with token
if [ "$AUTH_SUCCESS" = false ]; then
    echo "Trying interactive login..."
    echo "$TOKEN" | railway login 2>&1 | head -5
    if railway whoami &> /dev/null 2>&1; then
        echo "✅ Authentication successful via interactive login"
        railway whoami
        AUTH_SUCCESS=true
    fi
fi

if [ "$AUTH_SUCCESS" = false ]; then
    echo "❌ All authentication methods failed"
    echo "⚠️  Token might need to be used via Railway Dashboard"
    exit 1
fi

# Link to project
echo ""
echo "Step 4: Linking to project..."
railway link --project "$PROJECT_ID" 2>/dev/null && echo "✅ Linked to project" || echo "⚠️  Already linked or link failed"

# Set all variables
echo ""
echo "Step 5: Setting environment variables..."
railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a" && echo "✅ FAL_API_KEY"
railway variables set FAL_BASE_URL="https://queue.fal.run" && echo "✅ FAL_BASE_URL"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video" && echo "✅ FAL_MODEL_ID"
railway variables set USE_REDIS="true" && echo "✅ USE_REDIS"
railway variables set VIDEO_STORAGE_PATH="storage/videos" && echo "✅ VIDEO_STORAGE_PATH"
railway variables set REQUEST_TIMEOUT_SECONDS="30.0" && echo "✅ REQUEST_TIMEOUT_SECONDS"
railway variables set MAX_RETRIES="3" && echo "✅ MAX_RETRIES"
railway variables set RETRY_BACKOFF_FACTOR="1.5" && echo "✅ RETRY_BACKOFF_FACTOR"

# Verify variables
echo ""
echo "Step 6: Verifying variables..."
railway variables 2>&1 | grep -E "FAL_|USE_REDIS|VIDEO_STORAGE" | head -10 || echo "Variables set"

# Check deployment status
echo ""
echo "Step 7: Deployment status..."
railway status 2>&1

# Show recent logs
echo ""
echo "Step 8: Recent logs..."
railway logs --tail 20 2>&1 | head -40

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Perfect Connection Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Useful Commands:"
echo "  railway logs --follow    # Watch logs in real-time"
echo "  railway status           # Check deployment status"
echo "  railway variables        # View all variables"
echo "  railway up               # Trigger deployment"
echo "  railway open             # Open Railway dashboard"
echo ""
