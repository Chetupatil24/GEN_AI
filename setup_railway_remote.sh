#!/bin/bash
# Complete Railway Remote Setup Script
# This will guide you through connecting to Railway

PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 Railway Remote Connection Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check/Install Railway CLI
echo "Step 1: Installing Railway CLI..."
if command -v railway &> /dev/null; then
    echo "✅ Railway CLI already installed"
    railway --version
else
    if command -v npm &> /dev/null; then
        echo "📦 Installing Railway CLI..."
        npm i -g @railway/cli
        if [ $? -eq 0 ]; then
            echo "✅ Railway CLI installed successfully"
        else
            echo "❌ Failed to install Railway CLI"
            exit 1
        fi
    else
        echo "❌ npm not found. Please install Node.js first:"
        echo "   Visit: https://nodejs.org/"
        echo ""
        echo "Or install via package manager:"
        echo "   Ubuntu/Debian: sudo apt install nodejs npm"
        echo "   Or use nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
        exit 1
    fi
fi

echo ""
echo "Step 2: Logging in to Railway..."
echo "⚠️  This will open your browser for authentication"
echo "Press Enter to continue..."
read

railway login

if [ $? -eq 0 ]; then
    echo "✅ Successfully logged in"
    railway whoami
else
    echo "❌ Login failed. Please try again:"
    echo "   railway login"
    exit 1
fi

echo ""
echo "Step 3: Connecting to project..."
cd "$(dirname "$0")"
railway link "$PROJECT_ID"

if [ $? -eq 0 ]; then
    echo "✅ Connected to project: $PROJECT_ID"
else
    echo "⚠️  Project may already be linked or link failed"
fi

echo ""
echo "Step 4: Setting environment variables..."
echo "Setting required variables..."

railway variables set FAL_API_KEY="0d44c9a0-5679-4338-9f14-055fa0907d5f:6e3f241a600df52476c1bb414dff5e4a" 2>/dev/null && echo "✅ FAL_API_KEY set" || echo "⚠️  FAL_API_KEY may already be set"
railway variables set FAL_BASE_URL="https://queue.fal.run" 2>/dev/null && echo "✅ FAL_BASE_URL set" || echo "⚠️  FAL_BASE_URL may already be set"
railway variables set FAL_MODEL_ID="fal-ai/minimax-video" 2>/dev/null && echo "✅ FAL_MODEL_ID set" || echo "⚠️  FAL_MODEL_ID may already be set"
railway variables set USE_REDIS="true" 2>/dev/null && echo "✅ USE_REDIS set" || echo "⚠️  USE_REDIS may already be set"
railway variables set VIDEO_STORAGE_PATH="storage/videos" 2>/dev/null && echo "✅ VIDEO_STORAGE_PATH set" || echo "⚠️  VIDEO_STORAGE_PATH may already be set"

echo ""
echo "Step 5: Verifying connection..."
railway status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 You're now connected to Railway remotely!"
echo ""
echo "Useful commands:"
echo "  railway logs --follow    # Watch logs in real-time"
echo "  railway status            # Check project status"
echo "  railway variables         # View all variables"
echo "  railway up                # Deploy latest code"
echo "  railway open              # Open dashboard"
echo ""
