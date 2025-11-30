# 🎬 Pet Roast AI - Streamlit Web Interface

Beautiful web interface for generating AI-powered pet roast videos in multiple Indian languages.

## Features

- 🖼️ **Image Upload**: Upload your pet's photo
- ✍️ **Custom Roasts**: Write personalized roast text
- 🌐 **Multi-language Support**: Translate to 12+ Indian languages
- 🎭 **AR Filters**: Apply Banuba AR effects
- 🎥 **Video Generation**: Create roast videos via Revid.ai
- 📊 **Real-time Status**: Track video generation progress
- 🔄 **Auto-refresh**: Optional automatic status updates

## Quick Start

### 1. Start Backend Services

```bash
# Start IndicTrans2 (in one terminal)
cd IndicTrans2
INDICTRANS_MODE=mock python inference_server_simple.py

# Start FastAPI Backend (in another terminal)
cd /home/chetan-patil/myprojects/pet_roasts
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start Redis (if not already running)
sudo systemctl start redis-server
```

### 2. Launch Streamlit App

```bash
cd /home/chetan-patil/myprojects/pet_roasts
source .venv/bin/activate
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Usage Guide

### Step 1: Write Your Roast
- Enter a funny roast text about your pet
- Test translation to different languages
- Preview translated text

### Step 2: Upload Pet Image
- Click "Browse files" to upload
- Supported formats: JPG, PNG
- Image will be displayed as preview

### Step 3: Generate Video
- Both roast text and image must be provided
- Click "Generate Roast Video"
- Track status in real-time
- Download video when complete

## Configuration

### Language Options
- English
- Hindi (हिन्दी)
- Bengali (বাংলা)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Malayalam (മലയാളം)
- Kannada (ಕನ್ನಡ)
- Gujarati (ગુજરાતી)
- Marathi (मराठी)
- Punjabi (ਪੰਜਾਬੀ)
- Odia (ଓଡ଼ିଆ)
- Assamese (অসমীয়া)
- Urdu (اردو)

### AR Filters
- **Desi Fire**: Spicy overlays and glow effects
- **Pet Maharaja**: Regal royalty with ornate accessories
- **Bollywood Burn**: Cinematic lighting and spark particles

## System Requirements

### Backend Services
- FastAPI backend running on port 8000
- IndicTrans2 server on port 5000
- Redis server on port 6379

### Dependencies
- streamlit >= 1.28.0
- pillow >= 10.0.0
- requests
- All backend requirements

## Troubleshooting

### Backend Not Connected
**Error**: "⚠️ Backend server is not running!"

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/healthz

# If not, start it
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Translation Fails
**Error**: Translation API returns error

**Solution**:
```bash
# Check IndicTrans2 server
curl http://localhost:5000/healthz

# Restart if needed
cd IndicTrans2
INDICTRANS_MODE=mock python inference_server_simple.py
```

### Video Generation Stuck
**Issue**: Status shows "processing" for too long

**Solution**:
- Check `/tmp/backend.log` for errors
- Verify Revid.ai API key in `.env`
- Check Redis connection: `redis-cli ping`

### Port Already in Use
**Error**: `Address already in use`

**Solution**:
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run streamlit_app.py --server.port 8502
```

## Features Showcase

### Translation Testing
Test translations without generating videos:
1. Enter roast text
2. Select source and target languages
3. Click "Translate Text"
4. View original and translated text side-by-side

### Video Status Tracking
Real-time monitoring of video generation:
- **Queued** (25%): Job accepted, waiting in queue
- **Processing** (50%): Video being generated
- **Completed** (100%): Video ready for download
- **Failed**: Error occurred, check logs

### Auto-Refresh
Enable automatic status updates:
- Check "Auto-refresh status every 5 seconds"
- Automatically polls backend until completion
- Stops on completion or failure

## Architecture

```
┌─────────────┐
│  Browser    │
│ (Port 8501) │
└──────┬──────┘
       │ HTTP
       v
┌─────────────────┐
│   Streamlit     │
│   Frontend      │
└──────┬──────────┘
       │ REST API
       v
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│  (Port 8000)    │
└──────┬──────────┘
       │
       ├─────────────> IndicTrans2 (Port 5000)
       │
       ├─────────────> Revid.ai API
       │
       └─────────────> Redis (Port 6379)
```

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/healthz` | GET | Check backend health |
| `/api/translate-text` | POST | Translate text |
| `/api/generate-video` | POST | Create video job |
| `/api/video-status/{id}` | GET | Check job status |
| `/api/video-result/{id}` | GET | Get video URL |
| `/api/banuba-filters` | GET | List AR filters |

## Development

### Running in Development Mode

```bash
# Enable auto-reload
streamlit run streamlit_app.py --server.runOnSave true

# Disable CORS warnings
streamlit run streamlit_app.py --server.enableCORS false
```

### Customization

Edit `streamlit_app.py` to customize:
- UI colors and styling (CSS section)
- Language options (LANGUAGES dict)
- API endpoints (BACKEND_URL)
- Refresh intervals
- Status messages

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY streamlit_app.py .
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0"]
```

### Environment Variables

```bash
# Backend URL for production
BACKEND_URL=https://api.yourpetroast.com

# Streamlit config
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## Support

For issues:
1. Check backend logs: `tail -f /tmp/backend.log`
2. Check Streamlit logs in terminal
3. Verify all services are running
4. Test API endpoints directly with curl

## Credits

Built with:
- **Streamlit** - Interactive web interface
- **FastAPI** - Backend REST API
- **AI4Bharat IndicTrans2** - Translation
- **Revid.ai** - Video generation
- **Redis** - Job persistence
