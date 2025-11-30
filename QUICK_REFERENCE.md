# Pet Roast AI Backend - Quick Reference

## ✅ Successfully Integrated Components

### 1. IndicTrans2 (AI4Bharat Translation)
- **Location**: `/home/chetan-patil/myprojects/pet_roasts/IndicTrans2`
- **Server**: `inference_server_simple.py`
- **Port**: 5000
- **Mode**: MOCK (for testing) / FULL (for real translations)

### 2. FastAPI Backend
- **Port**: 8000
- **Health Check**: `http://localhost:8000/healthz`
- **API Docs**: `http://localhost:8000/docs`

## 🚀 Quick Start

### Option 1: Using Start Script (Recommended)
```bash
cd /home/chetan-patil/myprojects/pet_roasts
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Start IndicTrans2 Server:**
```bash
cd /home/chetan-patil/myprojects/pet_roasts/IndicTrans2
INDICTRANS_MODE=mock python inference_server_simple.py
```

**Terminal 2 - Start Backend Server:**
```bash
cd /home/chetan-patil/myprojects/pet_roasts
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### Translation
```bash
curl -X POST http://localhost:8000/api/translate-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "तुम्हारा कुत्ता बहुत प्यारा है",
    "source_lang": "hi",
    "target_lang": "en"
  }'
```

### Video Generation
```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your dog is very cute!",
    "image_url": "https://example.com/dog.jpg"
  }'
```

### Check Video Status
```bash
curl http://localhost:8000/api/video-status/{job_id}
```

### Get Video Result
```bash
curl http://localhost:8000/api/video-result/{job_id}
```

### List AR Filters
```bash
curl http://localhost:8000/api/banuba-filters
```

## 🧪 Testing

### Run All Tests
```bash
cd /home/chetan-patil/myprojects/pet_roasts
source .venv/bin/activate
pytest tests/test_api.py -v
```

### Test Individual Components

**Test IndicTrans2 Server:**
```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "नमस्ते",
    "source_language": "hi",
    "target_language": "en"
  }'
```

**Test Backend Health:**
```bash
curl http://localhost:8000/healthz
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# IndicTrans2 Configuration
AI4BHARAT_BASE_URL=http://localhost:5000
AI4BHARAT_TRANSLATE_PATH=/translate

# Revid.ai Configuration
REVID_API_KEY=your-revid-api-key

# Optional
REVID_WEBHOOK_SECRET=your-webhook-secret
MAX_RETRIES=3
RETRY_BACKOFF_FACTOR=1.5
```

## 🔄 Switching Modes

### MOCK Mode (Current - For Testing)
- Fast, no model loading
- Returns fake translations with suffix
- Use for development/testing

### FULL Mode (For Production)
- Uses real IndicTrans2 models
- Requires ~2GB disk space for models
- First run downloads models (~10 minutes)
- Accurate translations

**To switch to FULL mode:**
```bash
# Stop mock server
pkill -f inference_server_simple

# Start in FULL mode
cd /home/chetan-patil/myprojects/pet_roasts/IndicTrans2
INDICTRANS_MODE=full python inference_server_simple.py
```

## 📊 Service Status

### Check Running Services
```bash
# Check IndicTrans2 server
curl http://localhost:5000/health

# Check Backend server
curl http://localhost:8000/healthz

# Check all Python processes
ps aux | grep python | grep -E "(inference_server|uvicorn)"
```

### View Logs
```bash
# IndicTrans2 logs
tail -f /tmp/indictrans2.log

# Backend logs
tail -f /tmp/backend.log
```

### Stop Services
```bash
# Stop IndicTrans2 server
pkill -f inference_server_simple

# Stop Backend server
pkill -f "uvicorn app.main:app"
```

## 🐛 Troubleshooting

### IndicTrans2 Server Not Starting
1. Check logs: `cat /tmp/indictrans2.log`
2. Verify Python environment: `which python`
3. Test manually: `python IndicTrans2/inference_server_simple.py`

### Backend Can't Connect to IndicTrans2
1. Verify IndicTrans2 is running: `curl http://localhost:5000`
2. Check .env has correct URL: `AI4BHARAT_BASE_URL=http://localhost:5000`
3. Check firewall/ports: `netstat -tlnp | grep 5000`

### Tests Failing
1. Ensure both servers are running
2. Check .env has REVID_API_KEY set
3. Run tests with verbose output: `pytest tests/ -vv`

### Port Already in Use
```bash
# Find process using port
lsof -i :5000  # or :8000

# Kill the process
kill -9 <PID>
```

## 📚 Supported Languages

| Language | ISO Code | Example |
|----------|----------|---------|
| Hindi | hi | हिन्दी |
| Bengali | bn | বাংলা |
| Gujarati | gu | ગુજરાતી |
| Marathi | mr | मराठी |
| Kannada | kn | ಕನ್ನಡ |
| Telugu | te | తెలుగు |
| Malayalam | ml | മലയാളം |
| Tamil | ta | தமிழ் |
| Punjabi | pa | ਪੰਜਾਬੀ |
| Odia | or | ଓଡ଼ିଆ |
| Assamese | as | অসমীয়া |
| Urdu | ur | اردو |
| English | en | English |

## 🎯 Next Steps

1. ✅ Backend integrated with IndicTrans2
2. ✅ Webhook security implemented
3. ✅ Retry logic with exponential backoff
4. ✅ All tests passing (7/7)
5. ⏳ Replace in-memory JobStore with Redis/PostgreSQL
6. ⏳ Switch to FULL mode for production deployment
7. ⏳ Add caching layer for frequent translations

## 📞 Current Status

- **IndicTrans2 Server**: ✅ Running on port 5000 (MOCK mode)
- **Backend Server**: ✅ Running on port 8000
- **All Tests**: ✅ Passing (7/7)
- **Integration**: ✅ Complete and working
