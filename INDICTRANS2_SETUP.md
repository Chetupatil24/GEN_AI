# IndicTrans2 Setup Guide

This guide explains how to set up IndicTrans2 (AI4Bharat's multilingual translation engine) for the Pet Roast AI Backend.

## Prerequisites

- Python 3.7 or higher
- CUDA-capable GPU (recommended for faster inference, optional)
- Git

## Installation Steps

### 1. Clone IndicTrans2 Repository

```bash
# Navigate to a directory where you want to install IndicTrans2
cd ~/projects  # or your preferred location

# Clone the repository
git clone https://github.com/AI4Bharat/IndicTrans2
cd IndicTrans2
```

### 2. Install Dependencies

IndicTrans2 provides an installation script that sets up all required dependencies:

```bash
source install.sh
```

This script will:
- Create a Python virtual environment
- Install PyTorch and required ML libraries
- Download pre-trained model weights
- Set up the inference engine

**Note**: The installation may take 10-20 minutes depending on your internet connection and whether models need to be downloaded.

### 3. Start the Inference Server

Once installation is complete, start the IndicTrans2 inference server:

```bash
python inference/engine/server.py
```

The server will start on `http://localhost:5000` by default.

**Expected output:**
```
Loading model...
Model loaded successfully
Running on http://localhost:5000
```

### 4. Verify Installation

Test the IndicTrans2 server is running:

```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "आपका कुत्ता बहुत प्यारा है",
    "source_language": "hi",
    "target_language": "en"
  }'
```

Expected response:
```json
{
  "output": "Your dog is very cute"
}
```

## Configuration for Pet Roast Backend

### Update Environment Variables

The Pet Roast backend is already configured to use IndicTrans2. Verify your `.env` file contains:

```bash
AI4BHARAT_BASE_URL=http://localhost:5000
AI4BHARAT_TRANSLATE_PATH=/translate
```

### Supported Language Codes

IndicTrans2 supports the following Indian languages:

| Language | Code | Example |
|----------|------|---------|
| Hindi | `hi` | हिन्दी |
| Bengali | `bn` | বাংলা |
| Gujarati | `gu` | ગુજરાતી |
| Marathi | `mr` | मराठी |
| Kannada | `kn` | ಕನ್ನಡ |
| Telugu | `te` | తెలుగు |
| Malayalam | `ml` | മലയാളം |
| Tamil | `ta` | தமிழ் |
| Punjabi | `pa` | ਪੰਜਾਬੀ |
| Odia | `or` | ଓଡ଼ିଆ |
| Assamese | `as` | অসমীয়া |
| Urdu | `ur` | اردو |
| English | `en` | English |

## Running Both Services

### Terminal 1: IndicTrans2 Server
```bash
cd ~/projects/IndicTrans2  # or wherever you installed it
python inference/engine/server.py
```

### Terminal 2: Pet Roast Backend
```bash
cd /home/chetan-patil/myprojects/pet_roasts
source .venv/bin/activate
uvicorn app.main:app --reload
```

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, you can modify the IndicTrans2 server to use a different port:

```bash
python inference/engine/server.py --port 5001
```

Then update your `.env` file:
```bash
AI4BHARAT_BASE_URL=http://localhost:5001
```

### Model Loading Issues
If models fail to load, try re-running the installation:
```bash
cd IndicTrans2
rm -rf models/  # Remove existing models
source install.sh  # Reinstall
```

### GPU/CUDA Issues
IndicTrans2 works with both CPU and GPU. If you have CUDA errors:
- Ensure CUDA drivers are properly installed
- The system will fall back to CPU if GPU is unavailable (slower but functional)

### Connection Refused
If the backend can't connect to IndicTrans2:
1. Verify IndicTrans2 server is running: `curl http://localhost:5000`
2. Check firewall settings aren't blocking localhost connections
3. Verify the correct port in `.env` file

## Performance Optimization

### GPU Acceleration
For production workloads, use a CUDA-capable GPU:
- Reduces translation time from ~2-3 seconds to ~200-300ms
- Edit `inference/engine/server.py` to specify GPU device if you have multiple GPUs

### Batching
IndicTrans2 supports batch translation for improved throughput. Modify the client to send multiple texts in one request.

### Model Caching
Keep the IndicTrans2 server running continuously to avoid model reloading overhead (~10-30 seconds on startup).

## Alternative: Docker Deployment

For easier deployment, consider containerizing IndicTrans2:

```dockerfile
# Example Dockerfile for IndicTrans2
FROM python:3.9-slim

RUN apt-get update && apt-get install -y git

WORKDIR /app
RUN git clone https://github.com/AI4Bharat/IndicTrans2 .
RUN source install.sh

EXPOSE 5000
CMD ["python", "inference/engine/server.py"]
```

Build and run:
```bash
docker build -t indictrans2 .
docker run -p 5000:5000 indictrans2
```

## References

- [IndicTrans2 GitHub Repository](https://github.com/AI4Bharat/IndicTrans2)
- [AI4Bharat Official Website](https://ai4bharat.org/)
- [IndicTrans2 Paper](https://arxiv.org/abs/2305.16307)
