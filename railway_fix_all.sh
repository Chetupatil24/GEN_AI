#!/bin/bash
# Railway Connection & Fix All Script
# Project: pet_roasting
# Project ID: d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

set -e

PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"
ENVIRONMENT_ID="d07ed2df-e646-45dd-9510-b40b1ceee70d"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Railway Connection & Fix All"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "⚠️  Railway CLI not installed"
    echo ""
    echo "Installing Railway CLI..."
    if command -v npm &> /dev/null; then
        npm i -g @railway/cli
        echo "✅ Railway CLI installed"
    else
        echo "❌ npm not found. Please install Node.js first:"
        echo "   https://nodejs.org/"
        echo ""
        echo "Or use Railway Dashboard:"
        echo "   https://railway.app/project/$PROJECT_ID"
        exit 1
    fi
fi

echo "✅ Railway CLI detected"
echo ""

# Check if logged in
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "⚠️  Not logged in to Railway"
    echo "Opening Railway login..."
    railway login
else
    echo "✅ Already logged in"
    railway whoami
fi

echo ""
echo "🔗 Linking to project..."
railway link "$PROJECT_ID" 2>/dev/null || echo "⚠️  Project may already be linked"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 Checking Project Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check project status
echo "Project Status:"
railway status || echo "⚠️  Could not get status"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔍 Checking Environment Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check required variables
REQUIRED_VARS=(
    "FAL_API_KEY"
    "FAL_BASE_URL"
    "FAL_MODEL_ID"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if railway variables get "$var" &> /dev/null; then
        echo "✅ $var is set"
    else
        echo "❌ $var is MISSING"
        MISSING_VARS+=("$var")
    fi
done

echo ""

# Set missing variables
if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "🔧 Setting missing environment variables..."
    echo ""
    
    for var in "${MISSING_VARS[@]}"; do
        case $var in
            "FAL_API_KEY")
                echo "Setting FAL_API_KEY..."
                railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
                ;;
            "FAL_BASE_URL")
                echo "Setting FAL_BASE_URL..."
                railway variables set FAL_BASE_URL="https://queue.fal.run"
                ;;
            "FAL_MODEL_ID")
                echo "Setting FAL_MODEL_ID..."
                railway variables set FAL_MODEL_ID="fal-ai/minimax-video"
                ;;
        esac
    done
    
    echo ""
    echo "✅ Environment variables set"
else
    echo "✅ All required variables are set"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📋 Setting Optional Variables"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Set optional but recommended variables
OPTIONAL_VARS=(
    "USE_REDIS=true"
    "VIDEO_STORAGE_PATH=storage/videos"
    "REQUEST_TIMEOUT_SECONDS=30.0"
    "MAX_RETRIES=3"
    "RETRY_BACKOFF_FACTOR=1.5"
)

for var in "${OPTIONAL_VARS[@]}"; do
    key="${var%%=*}"
    value="${var#*=}"
    if ! railway variables get "$key" &> /dev/null; then
        echo "Setting $key=$value..."
        railway variables set "$key"="$value"
    else
        echo "✅ $key already set"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 Viewing Recent Logs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Recent logs (last 20 lines):"
railway logs --tail 20 || echo "⚠️  Could not fetch logs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Deployment Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "To redeploy, run:"
echo "  railway up"
echo ""
echo "Or trigger redeploy from Railway Dashboard:"
echo "  https://railway.app/project/$PROJECT_ID/deployments"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Fix Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Check deployment status:"
echo "   railway status"
echo ""
echo "2. Monitor logs:"
echo "   railway logs"
echo ""
echo "3. Open in browser:"
echo "   railway open"
echo ""
echo "4. Test health endpoint:"
echo "   Get URL from: railway open"
echo "   Then: curl https://your-app.railway.app/healthz"
echo ""
echo "✅ All fixes applied!"
echo ""
