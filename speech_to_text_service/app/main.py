from fastapi import FastAPI, Request
import tempfile, os, asyncio
from speech_to_text_service.services.whisper_transcriber import WhisperTranscriber
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

app = FastAPI()

@app.post("/transcribe")
async def transcribe(request: Request):
    audio_bytes = await request.body()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
        tmp.write(audio_bytes)
        temp_path = tmp.name

    transcriber = WhisperTranscriber()
    result = await transcriber.transcribe(temp_path)

    await asyncio.to_thread(os.remove, temp_path)

    return result
