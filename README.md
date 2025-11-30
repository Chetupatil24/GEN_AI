# Pet Roast AI Backend

FastAPI backend orchestrating IndicTrans2 (AI4Bharat) multilingual translation, Revid.ai video generation, and a curated AR filter catalog for the hybrid pet roasting application.

## Features

- **IndicTrans2 Integration** for multilingual translation supporting 12+ Indian languages (Hindi, Bengali, Gujarati, Marathi, Kannada, Telugu, Malayalam, Tamil, Punjabi, Odia, Assamese, Urdu).
- Revid.ai orchestration for async AI video generation workflows with webhook support and signature verification.
- Banuba AR filter catalog exposure for front-end selection (filters applied client-side).
- RESTful JSON API with validation, retry logic, and structured error handling.

## Getting Started

### 1. Setup IndicTrans2 (AI4Bharat Translation Engine)

Clone and install IndicTrans2 from AI4Bharat:

```bash
# Clone the IndicTrans2 repository
git clone https://github.com/AI4Bharat/IndicTrans2
cd IndicTrans2

# Install dependencies
source install.sh

# Start the inference server (runs on http://localhost:5000)
python inference/engine/server.py
```

The IndicTrans2 server must be running before starting the FastAPI backend.

### 2. Setup Backend Application

Navigate back to the project directory:

```bash
cd /home/chetan-patil/myprojects/pet_roasts
```

**Create and activate a virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Configure environment variables** (`.env` file):
- `REVID_API_KEY` - Your Revid.ai API key (required)
- `AI4BHARAT_BASE_URL` - IndicTrans2 server URL (default: `http://localhost:5000`)
- `AI4BHARAT_TRANSLATE_PATH` - Translation endpoint path (default: `/translate`)
- `REVID_WEBHOOK_SECRET` - Optional webhook signature secret for production

**Run the development server**:
```bash
uvicorn app.main:app --reload
```

Server will start on `http://localhost:8000`

## API Overview

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/translate-text` | POST | Translate or analyse roast text with AI4Bharat |
| `/api/generate-video` | POST | Submit roast script and pet image for AI video creation |
| `/api/video-status/{job_id}` | GET | Poll Revid.ai job status |
| `/api/video-result/{job_id}` | GET | Retrieve final video URL when ready |
| `/api/banuba-filters` | GET | List curated Banuba AR filters |
| `/api/revid-webhook` | POST | Receive asynchronous callbacks from Revid.ai |
| `/healthz` | GET | Health probe for orchestration |

## Example Usage

**Translate Hindi text to English:**
```bash
curl -X POST http://localhost:8000/api/translate-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Ye doggo bada swag hai", "source_lang": "hi", "target_lang": "en"}'
```

**Generate AI video from translated roast:**
```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This doggo has too much swag!",
    "image_url": "https://example.com/pet.jpg"
  }'
```

## Supported Languages

IndicTrans2 supports translation between:
- **Hindi** (hi)
- **Bengali** (bn)
- **Gujarati** (gu)
- **Marathi** (mr)
- **Kannada** (kn)
- **Telugu** (te)
- **Malayalam** (ml)
- **Tamil** (ta)
- **Punjabi** (pa)
- **Odia** (or)
- **Assamese** (as)
- **Urdu** (ur)
- **English** (en)

## Production Features

✅ **Webhook Signature Verification** - HMAC-SHA256 validation for Revid.ai callbacks
✅ **Retry Logic** - Exponential backoff for transient failures (3 retries, 1.5x backoff)
✅ **CORS Support** - Cross-origin requests enabled
✅ **Health Checks** - `/healthz` endpoint for orchestrators

## Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - ⭐ Quick reference for common tasks and troubleshooting
- **[INDICTRANS2_SETUP.md](INDICTRANS2_SETUP.md)** - Detailed IndicTrans2 installation and setup guide
- **[INDICTRANS2_INTEGRATION.md](INDICTRANS2_INTEGRATION.md)** - Technical integration details and API reference
- **[start.sh](start.sh)** - Quick start script to launch both IndicTrans2 and backend servers

## Quick Start

```bash
# Make start script executable (first time only)
chmod +x start.sh

# Start everything (IndicTrans2 + Backend)
./start.sh
```

### Manual Start (Alternative)

**Terminal 1 - IndicTrans2 Server:**
```bash
cd IndicTrans2
INDICTRANS_MODE=mock python inference_server_simple.py
```

**Terminal 2 - Backend Server:**
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

### Verify Setup

```bash
# Test IndicTrans2
curl http://localhost:5000

# Test Backend
curl http://localhost:8000/healthz

# Run tests
pytest tests/test_api.py -v
```

## Next Steps

- Replace the in-memory job store with persistent storage (Redis, PostgreSQL, etc.)
- Scale IndicTrans2 inference with GPU acceleration
- Add caching layer for frequently translated phrases
- Implement rate limiting and request quotas
# GEN_AI
# GEN_AI
