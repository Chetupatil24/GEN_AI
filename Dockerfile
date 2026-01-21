# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download YOLO model at build time (with error handling)
# If this fails, the model will be downloaded at runtime
RUN python -c "import torch; torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)" || echo "YOLO model download failed, will download at runtime"

# Copy application code
COPY app/ ./app/
COPY IndicTrans2/ ./IndicTrans2/

# Create necessary directories with proper permissions
RUN mkdir -p logs storage/videos && \
    chmod -R 755 storage logs

# Railway automatically sets PORT, so we use environment variable
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["sh", "-c", "curl -f http://localhost:${PORT:-8000}/healthz || exit 1"]

# Run the application (Railway will override with PORT env var)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
