#!/bin/bash

# Quick Start Script for Pet Roast AI Backend with IndicTrans2

echo "=== Pet Roast AI Backend - IndicTrans2 Quick Start ==="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
INDICTRANS2_DIR="${SCRIPT_DIR}/IndicTrans2"

# Check if IndicTrans2 directory exists
if [ ! -d "$INDICTRANS2_DIR" ]; then
    echo "❌ IndicTrans2 not found at $INDICTRANS2_DIR"
    echo ""
    echo "Please install IndicTrans2 first:"
    echo "  cd ${SCRIPT_DIR}"
    echo "  git clone https://github.com/AI4Bharat/IndicTrans2"
    echo "  cd IndicTrans2"
    echo "  source install.sh"
    echo ""
    echo "See INDICTRANS2_SETUP.md for detailed instructions."
    exit 1
fi

echo "✅ IndicTrans2 found at $INDICTRANS2_DIR"
echo ""

# Check if IndicTrans2 server is running
if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "✅ IndicTrans2 server is already running on http://localhost:5000"
else
    echo "⚠️  IndicTrans2 server is not running"
    echo ""
    echo "Starting IndicTrans2 server in background..."
    echo "This may take 30-120 seconds for model loading (first time may download models)..."

    cd "$INDICTRANS2_DIR"
    # Start in MOCK mode for testing (set INDICTRANS_MODE=full for real translations)
    INDICTRANS_MODE=mock nohup python inference_server_simple.py > /tmp/indictrans2.log 2>&1 &
    INDICTRANS2_PID=$!
    echo "IndicTrans2 server started (PID: $INDICTRANS2_PID)"
    echo "Logs: tail -f /tmp/indictrans2.log"
    echo ""
    echo "📝 Note: Running in MOCK mode for testing."
    echo "   Mock mode returns fake translations for development."
    echo "   For real translations, stop the server and run:"
    echo "   INDICTRANS_MODE=full python ${INDICTRANS2_DIR}/inference_server_simple.py"
    echo ""

    # Wait for server to be ready
    echo "Waiting for server to be ready..."
    for i in {1..60}; do
        if curl -s http://localhost:5000 > /dev/null 2>&1; then
            echo ""
            echo "✅ IndicTrans2 server is ready!"
            break
        fi
        if [ $((i % 5)) -eq 0 ]; then
            echo -n " ${i}s"
        else
            echo -n "."
        fi
        sleep 2
    done
    echo ""
fi

echo ""
echo "=== Starting Pet Roast Backend ==="
echo ""

# Go back to the project root
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your REVID_API_KEY"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "✅ Virtual environment activated"
echo ""

# Run tests
echo "Running tests..."
pytest tests/test_api.py -v

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed!"
    echo ""
    echo "=== Starting Development Server ==="
    echo ""
    echo "Backend will be available at: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Health Check: http://localhost:8000/healthz"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo ""
    echo "❌ Tests failed. Please fix errors before starting the server."
    exit 1
fi
