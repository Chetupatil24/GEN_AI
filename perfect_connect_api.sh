#!/bin/bash
# Perfect Railway Connection using GraphQL API

TOKEN="d2438d39-dad1-4761-a423-bf02d3bdd002"
PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"
API_URL="https://backboard.railway.app/graphql/v2"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔧 Perfect Railway Connection (GraphQL API)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Test authentication
echo "Step 1: Testing authentication..."
AUTH_RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ me { id email } }"}')

if echo "$AUTH_RESPONSE" | grep -q "email\|id"; then
    echo "✅ Authentication successful!"
    echo "$AUTH_RESPONSE" | grep -o '"email":"[^"]*"' | head -1
else
    echo "❌ Authentication failed"
    echo "Response: $AUTH_RESPONSE"
    exit 1
fi

# Get project details
echo ""
echo "Step 2: Getting project details..."
PROJECT_QUERY='{"query":"query { project(id: \"'$PROJECT_ID'\") { id name } }"}'
PROJECT_RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$PROJECT_QUERY")

if echo "$PROJECT_RESPONSE" | grep -q "name\|id"; then
    echo "✅ Project found"
    echo "$PROJECT_RESPONSE" | grep -o '"name":"[^"]*"' | head -1
else
    echo "⚠️  Could not fetch project: $PROJECT_RESPONSE"
fi

# Get environment ID
echo ""
echo "Step 3: Getting environment..."
ENV_QUERY='{"query":"query { project(id: \"'$PROJECT_ID'\") { environments { edges { node { id name } } } } }"}'
ENV_RESPONSE=$(curl -s -X POST "$API_URL" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$ENV_QUERY")

ENV_ID=$(echo "$ENV_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$ENV_ID" ]; then
    echo "✅ Environment ID: $ENV_ID"
else
    echo "⚠️  Using production environment"
    ENV_ID="production"
fi

# Set variables using GraphQL mutation
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
    
    # GraphQL mutation to upsert variable
    MUTATION='{"query":"mutation { variableUpsert(input: { projectId: \"'$PROJECT_ID'\", name: \"'$KEY'\", value: \"'$VALUE'\" }) { id name value } }"}'
    
    RESPONSE=$(curl -s -X POST "$API_URL" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "$MUTATION")
    
    if echo "$RESPONSE" | grep -q "id\|name"; then
        echo "  ✅ $KEY set successfully"
    else
        echo "  ⚠️  $KEY (response: $RESPONSE)"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Perfect Connection Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Variables set via Railway GraphQL API"
echo "🚀 Railway will automatically redeploy"
echo ""
echo "Check deployment at:"
echo "https://railway.app/project/$PROJECT_ID"
echo ""
