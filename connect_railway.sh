#!/bin/bash
# Railway Remote Connection Script (Like SSH)
# Project: pet_roasting
# Project ID: d3e9f8f4-cdca-4825-9ec4-f7fa9844d266

PROJECT_ID="d3e9f8f4-cdca-4825-9ec4-f7fa9844d266"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🔌 Railway Remote Connection (Like SSH)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    if command -v npm &> /dev/null; then
        npm i -g @railway/cli
        echo "✅ Railway CLI installed"
    else
        echo "❌ npm not found. Please install Node.js:"
        echo "   https://nodejs.org/"
        exit 1
    fi
fi

echo "✅ Railway CLI ready"
echo ""

# Check if logged in
echo "🔐 Checking authentication..."
if ! railway whoami &> /dev/null; then
    echo "⚠️  Not logged in. Logging in now..."
    railway login
else
    USER=$(railway whoami 2>/dev/null | head -1)
    echo "✅ Logged in as: $USER"
fi

echo ""
echo "🔗 Connecting to project..."
cd "$(dirname "$0")"
railway link "$PROJECT_ID" 2>/dev/null || echo "✅ Already linked to project"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Connected to Railway!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Available Commands (Like SSH):"
echo ""
echo "  Status & Info:"
echo "    railway status              # Check project status"
echo "    railway whoami              # Current user"
echo "    railway variables           # List all variables"
echo ""
echo "  Logs (Like tail -f):"
echo "    railway logs                # View logs"
echo "    railway logs --tail 50     # Last 50 lines"
echo "    railway logs --follow      # Follow logs (real-time)"
echo ""
echo "  Variables (Like env):"
echo "    railway variables set KEY=\"value\"  # Set variable"
echo "    railway variables get KEY           # Get variable"
echo ""
echo "  Deployment:"
echo "    railway up                  # Deploy"
echo "    railway open                # Open dashboard"
echo ""
echo "  Remote Execution:"
echo "    railway run <command>       # Run command remotely"
echo "    railway run bash            # Interactive shell"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎯 Quick Actions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Check status:"
echo "   railway status"
echo ""
echo "2. View logs:"
echo "   railway logs --tail 50"
echo ""
echo "3. Check variables:"
echo "   railway variables"
echo ""
echo "4. Deploy:"
echo "   railway up"
echo ""
echo "✅ You're connected! Use commands above to manage Railway."
echo ""
