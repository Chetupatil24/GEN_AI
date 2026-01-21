#!/bin/bash
# Connect to Railway using API and fix all

TOKEN="d2438d39-dad1-4761-a423-bf02d3bdd002"
PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"
API_BASE="https://api.railway.app/v1"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Railway Connection via API & Fix All"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test authentication
echo "Step 1: Testing authentication..."
USER_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/user" 2>&1)
if echo "$USER_RESPONSE" | grep -q "email\|id"; then
    echo "✅ Authentication successful"
    echo "$USER_RESPONSE" | grep -o '"email":"[^"]*"' | head -1
else
    echo "❌ Authentication failed"
    echo "Response: $USER_RESPONSE"
    exit 1
fi

# Get project details
echo ""
echo "Step 2: Getting project details..."
PROJECT_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/project/$PROJECT_ID" 2>&1)
if echo "$PROJECT_RESPONSE" | grep -q "id\|name"; then
    echo "✅ Project found"
    echo "$PROJECT_RESPONSE" | grep -o '"name":"[^"]*"' | head -1
else
    echo "⚠️  Could not fetch project details"
fi

# Get environment ID
echo ""
echo "Step 3: Getting environment ID..."
ENV_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_BASE/project/$PROJECT_ID/environments" 2>&1)
ENV_ID=$(echo "$ENV_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$ENV_ID" ]; then
    echo "✅ Environment ID: $ENV_ID"
else
    echo "⚠️  Using default environment"
    ENV_ID="production"
fi

# Set variables
echo ""
echo "Step 4: Setting environment variables..."

VARS=(
    "FAL_API_KEY=0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a"
    "FAL_BASE_URL=https://queue.fal.run"
    "FAL_MODEL_ID=fal-ai/minimax-video"
    "USE_REDIS=true"
    "VIDEO_STORAGE_PATH=storage/videos"
)

for var in "${VARS[@]}"; do
    KEY="${var%%=*}"
    VALUE="${var#*=}"
    echo "Setting $KEY..."
    RESPONSE=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$KEY\",\"value\":\"$VALUE\"}" \
        "$API_BASE/project/$PROJECT_ID/variables" 2>&1)
    if echo "$RESPONSE" | grep -q "id\|name"; then
        echo "  ✅ $KEY set"
    else
        echo "  ⚠️  $KEY (may already exist or need update)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ API Connection Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next: Check Railway Dashboard for deployment"
echo ""
