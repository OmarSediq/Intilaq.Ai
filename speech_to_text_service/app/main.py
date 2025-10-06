# speech_to_text_service/app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from speech_to_text_service.services.whisper_transcriber import WhisperTranscriber
from contextlib import asynccontextmanager
from speech_to_text_service.services.tracing import setup_tracing
import os

# instrumentation imports (we will call them BEFORE server start)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

transcriber: WhisperTranscriber = None

# --- Read env / decide tracing before creating app ---
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() in ("1", "true", "yes")
SERVICE_NAME = os.getenv("SERVICE_NAME", "whisper-service")

# Setup tracing provider (no-op if setup_tracing handles enabled flag)
# Recommended: make setup_tracing accept enabled kwarg (see example below)
setup_tracing(service_name=SERVICE_NAME, enabled=ENABLE_TRACING)

# Create app
app = FastAPI()

# Instrument app BEFORE it starts (so middleware is added during setup, not at runtime)
if ENABLE_TRACING:
    FastAPIInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcriber

    # app-specific startup
    transcriber = WhisperTranscriber()
    print("Whisper model loaded and cached once.")

    yield

# attach lifespan
app.router.lifespan_context = lifespan  # alternative to FastAPI(lifespan=...), equivalent attachment
# Or: app = FastAPI(lifespan=lifespan) — if you prefer, but we already created app above.

@app.post("/api/transcribe", tags=["Speech to Text"])
async def transcribe(request: Request):
    try:
        audio_bytes = await request.body()
        result = await transcriber.transcribe_bytes(audio_bytes)

        if not isinstance(result, dict) or "text" not in result:
            return JSONResponse(
                content={"text": "", "error": "[Whisper Error] Invalid response format"},
                status_code=200
            )

        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        print("Whisper Exception:", str(e))
        return JSONResponse(
            content={"text": "", "error": f"[Whisper Error] Exception: {str(e)}"},
            status_code=200
        )
