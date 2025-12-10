#!/bin/bash
# Quick setup script for configuring backend integration

set -e

echo "🔧 Pet Roast AI - Backend Integration Setup"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
else
    echo "Creating .env file from template..."
    cp .env.railway .env
fi

echo ""
echo "Please provide the following information:"
echo ""

# Get Revid API key
read -p "Enter your Revid.ai API key: " REVID_API_KEY
if [ -z "$REVID_API_KEY" ]; then
    echo -e "${RED}❌ Revid API key is required${NC}"
    exit 1
fi

# Get backend webhook URL
echo ""
echo "Enter your Railway backend webhook URL"
echo "Example: https://your-backend.railway.app/webhooks/pet-roast-complete"
read -p "Backend webhook URL: " BACKEND_WEBHOOK_URL

if [ -z "$BACKEND_WEBHOOK_URL" ]; then
    echo -e "${YELLOW}⚠️  No backend webhook URL provided${NC}"
    echo "You can add it later by setting BACKEND_WEBHOOK_URL in .env"
fi

# Get CORS origins
echo ""
echo "Enter your backend URL for CORS (press Enter for default '*')"
echo "Example: https://your-backend.railway.app"
read -p "Backend URL for CORS: " BACKEND_CORS_URL

if [ -z "$BACKEND_CORS_URL" ]; then
    CORS_ORIGINS='["*"]'
else
    CORS_ORIGINS="[\"${BACKEND_CORS_URL}\"]"
fi

# Get Redis URL
echo ""
echo "Enter Redis URL (press Enter to use Railway addon default)"
read -p "Redis URL: " REDIS_URL

if [ -z "$REDIS_URL" ]; then
    REDIS_URL="redis://default:password@redis.railway.internal:6379"
    echo -e "${YELLOW}Using Railway Redis addon URL (configure in Railway dashboard)${NC}"
fi

# Update .env file
cat > .env << EOF
# Revid.ai API Configuration
REVID_API_KEY=${REVID_API_KEY}
REVID_BASE_URL=https://api.revid.ai/v1
REVID_WEBHOOK_SECRET=

# Backend Integration
BACKEND_WEBHOOK_URL=${BACKEND_WEBHOOK_URL}
CORS_ORIGINS=${CORS_ORIGINS}

# Redis Configuration
REDIS_URL=${REDIS_URL}
USE_REDIS=true
REDIS_JOB_TTL_SECONDS=604800

# AI4Bharat Configuration (optional)
AI4BHARAT_BASE_URL=http://localhost:5000
AI4BHARAT_API_KEY=

# Request Configuration
REQUEST_TIMEOUT_SECONDS=30.0
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
EOF

echo ""
echo -e "${GREEN}✅ Configuration saved to .env${NC}"
echo ""
echo "Configuration summary:"
echo "======================"
echo "Revid API Key: ${REVID_API_KEY:0:10}..."
echo "Backend Webhook: ${BACKEND_WEBHOOK_URL:-'Not configured'}"
echo "CORS Origins: ${CORS_ORIGINS}"
echo "Redis URL: ${REDIS_URL}"
echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy to Railway: railway up"
echo "2. Add Redis addon in Railway dashboard"
echo "3. Test integration: python test_integration.py --ai-service-url <your-url>"
echo ""
echo "For detailed backend integration, see:"
echo "📖 BACKEND_INTEGRATION.md"
