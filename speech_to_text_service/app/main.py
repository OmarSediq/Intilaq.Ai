from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from speech_to_text_service.services.whisper_transcriber import WhisperTranscriber
from contextlib import asynccontextmanager
from speech_to_text_service.services.tracing import setup_tracing
import os
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

transcriber: WhisperTranscriber = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcriber

    # --- Tracing setup ---
    enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() in ("1","true","yes")
    setup_tracing(service_name=os.getenv("SERVICE_NAME", "whisper-service"), enabled=enable_tracing)

    if enable_tracing:
        # instrument FastAPI and outgoing HTTP requests (httpx / requests)
        FastAPIInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()

    # app-specific startup
    transcriber = WhisperTranscriber()
    print("Whisper model loaded and cached once.")

    yield

app = FastAPI(lifespan=lifespan)

@app.post("/api/transcribe" , tags=["Speech to Text"])
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
