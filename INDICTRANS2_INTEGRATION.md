# IndicTrans2 API Integration Details

This document explains the integration between the Pet Roast AI Backend and IndicTrans2's translation API.

## Architecture Overview

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│                 │      │                  │      │                 │
│  Client (Web/   │────▶│  FastAPI Backend │────▶│   IndicTrans2   │
│  Mobile App)    │      │  (Port 8000)     │      │   (Port 5000)   │
│                 │◀────│                  │◀────│                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                   │
                                   │
                                   ▼
                         ┌──────────────────┐
                         │                  │
                         │   Revid.ai API   │
                         │  (Video Gen)     │
                         │                  │
                         └──────────────────┘
```

## API Request Flow

### 1. Translation Request

**Client → Backend:**
```http
POST /api/translate-text
Content-Type: application/json

{
  "text": "आपका कुत्ता बहुत मज़ेदार है",
  "source_lang": "hi",
  "target_lang": "en"
}
```

**Backend → IndicTrans2:**
```http
POST http://localhost:5000/translate
Content-Type: application/json

{
  "input": "आपका कुत्ता बहुत मज़ेदार है",
  "source_language": "hi",
  "target_language": "en"
}
```

**IndicTrans2 → Backend:**
```json
{
  "output": "Your dog is very funny"
}
```

**Backend → Client (Normalized Response):**
```json
{
  "translated_text": "Your dog is very funny",
  "source_language": "hi",
  "target_language": "en",
  "task": "translation"
}
```

### 2. Video Generation Request

**Client → Backend:**
```http
POST /api/generate-video
Content-Type: application/json

{
  "text": "तुम्हारा कुत्ता बहुत आलसी है",
  "image_url": "https://example.com/pet.jpg"
}
```

**Backend Processing:**
1. Detect language is Hindi (`hi`)
2. Translate to English via IndicTrans2:
   - Input: "तुम्हारा कुत्ता बहुत आलसी है"
   - Output: "Your dog is very lazy"
3. Submit English text + image to Revid.ai
4. Store job in JobStore
5. Return job ID to client

**Backend → Client:**
```json
{
  "job_id": "job-123",
  "status": "queued",
  "message": "Video generation started"
}
```

## API Endpoint Changes

### Modified: `AI4BharatClient.translate_text()`

**Old Format (Generic AI4Bharat):**
```python
payload = {
    "text": text,
    "target_language": target_language,
    "task": task,
    "source_language": source_language  # optional
}
```

**New Format (IndicTrans2):**
```python
payload = {
    "input": text,
    "source_language": source_language or "auto",
    "target_language": target_language
}
```

**Response Normalization:**
```python
# IndicTrans2 returns: {"output": "translated text"}
# Backend normalizes to:
{
    "translated_text": result["output"],
    "source_language": source_language or "auto",
    "target_language": target_language,
    "task": "translation"
}
```

## Configuration Changes

### Environment Variables

| Variable | Old Value | New Value |
|----------|-----------|-----------|
| `AI4BHARAT_BASE_URL` | `http://localhost:8001` | `http://localhost:5000` |
| `AI4BHARAT_TRANSLATE_PATH` | `/v1/translate` | `/translate` |
| `AI4BHARAT_API_KEY` | Required | Not used (IndicTrans2 is local) |

### Settings Class

```python
# app/core/config.py
class Settings(BaseSettings):
    ai4bharat_base_url: str = "http://localhost:5000"  # Changed
    ai4bharat_translate_path: str = "/translate"       # Changed
    ai4bharat_api_key: Optional[str] = None            # Now optional
```

## Language Support

### Supported Language Codes

IndicTrans2 supports bidirectional translation between:

- `hi` - Hindi (हिन्दी)
- `bn` - Bengali (বাংলা)
- `gu` - Gujarati (ગુજરાતી)
- `mr` - Marathi (मराठी)
- `kn` - Kannada (ಕನ್ನಡ)
- `te` - Telugu (తెలుగు)
- `ml` - Malayalam (മലയാളം)
- `ta` - Tamil (தமிழ்)
- `pa` - Punjabi (ਪੰਜਾਬੀ)
- `or` - Odia (ଓଡ଼ିଆ)
- `as` - Assamese (অসমীয়া)
- `ur` - Urdu (اردو)
- `en` - English

### Automatic Language Detection

When `source_language` is not specified or set to `"auto"`, IndicTrans2 will attempt to detect the source language automatically.

```python
# Client can omit source_lang
POST /api/translate-text
{
  "text": "આ કૂતરું ખૂબ સુંદર છે",
  "target_lang": "en"
}

# Backend sends to IndicTrans2
{
  "input": "આ કૂતરું ખૂબ સુંદર છે",
  "source_language": "auto",
  "target_language": "en"
}
```

## Error Handling

### IndicTrans2 Connection Errors

If IndicTrans2 server is not running:

```python
# Retry logic kicks in (3 attempts with exponential backoff)
# After max retries:
raise AI4BharatAPIError(
    "AI4Bharat request failed after 3 attempts"
)
```

**HTTP Response:**
```json
{
  "detail": "AI4Bharat request error: connection refused"
}
```

### Unsupported Language

If client requests unsupported language:

```python
# Pydantic validation fails before reaching IndicTrans2
raise HTTPException(
    status_code=422,
    detail="Unsupported language code"
)
```

## Testing with IndicTrans2

### Unit Tests

Tests use `FakeAI4BharatClient` stub that simulates IndicTrans2 responses:

```python
class FakeAI4BharatClient:
    async def translate_text(self, *, text, source_language=None, target_language="en", task="translation"):
        return {
            "translated_text": f"{text} (translated to {target_language})",
            "source_language": source_language or "auto",
            "target_language": target_language,
            "task": task,
        }
```

### Integration Testing

To test with real IndicTrans2:

```bash
# 1. Start IndicTrans2 server
cd ~/projects/IndicTrans2
python inference/engine/server.py

# 2. Update test to use real client (remove dependency override)

# 3. Run integration tests
pytest tests/test_api.py -v -k translate
```

## Performance Considerations

### Translation Latency

- **CPU-only**: ~2-3 seconds per translation
- **With GPU**: ~200-300ms per translation

### Recommendations

1. **Keep IndicTrans2 Running**: Model loading takes 10-30 seconds at startup
2. **Use GPU**: Significant performance improvement for production
3. **Cache Translations**: Consider caching common phrases to reduce load
4. **Batch Requests**: IndicTrans2 supports batch translation for better throughput

### Monitoring

Monitor IndicTrans2 health:

```bash
# Check if server is responding
curl http://localhost:5000

# View server logs
tail -f /tmp/indictrans2.log  # If using start.sh script
```

## Migration from Previous Setup

### Breaking Changes

1. **Endpoint URL Changed**: `http://localhost:8001/v1/translate` → `http://localhost:5000/translate`
2. **Request Format**: `{"text": ...}` → `{"input": ...}`
3. **API Key**: No longer required for local IndicTrans2 deployment

### Backward Compatibility

The backend normalizes IndicTrans2 responses to maintain the same client-facing API contract:

✅ **No changes required in frontend/mobile apps**
✅ **Same REST API endpoints**
✅ **Same response format**

## Troubleshooting

### IndicTrans2 Server Not Responding

```bash
# Check if server is running
curl http://localhost:5000

# Check logs
cat /tmp/indictrans2.log

# Restart server
pkill -f "inference/engine/server.py"
cd ~/projects/IndicTrans2
python inference/engine/server.py
```

### Translation Quality Issues

- Verify correct language codes are being used
- Check input text encoding (must be UTF-8)
- Some informal/slang text may not translate accurately

### Performance Issues

- Check if GPU is being utilized: `nvidia-smi`
- Monitor system resources: `htop`
- Consider scaling IndicTrans2 horizontally for high load

## References

- [IndicTrans2 GitHub](https://github.com/AI4Bharat/IndicTrans2)
- [Backend Configuration](app/core/config.py)
- [AI4Bharat Client](app/clients/ai4bharat.py)
- [API Routes](app/api/routes.py)
