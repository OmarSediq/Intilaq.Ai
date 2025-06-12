from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from speech_to_text_service.services.whisper_transcriber import WhisperTranscriber
from contextlib import asynccontextmanager

transcriber: WhisperTranscriber = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global transcriber
    transcriber = WhisperTranscriber()
    print("Whisper model loaded and cached once.")
    yield


app = FastAPI(lifespan=lifespan)

@app.post("/transcribe")
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
