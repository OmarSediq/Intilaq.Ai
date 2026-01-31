import httpx
import tempfile
import os
import shutil
import asyncio
from fastapi import UploadFile
from backend.core.base_service import TraceableService

class WhisperTranscriberService(TraceableService):
    def __init__(self, http_client: httpx.AsyncClient, whisper_url: str):
        self._client = http_client
        self.whisper_url = whisper_url

    async def transcribe_audio(self, file: UploadFile) -> dict:
        input_path = None
        try:
            ext = os.path.splitext(file.filename)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
                await asyncio.to_thread(shutil.copyfileobj, file.file, temp_audio)
                input_path = temp_audio.name

            audio_bytes = await asyncio.to_thread(lambda: open(input_path, "rb").read())

            content_type = {
                ".mp3": "audio/mpeg",
                ".wav": "audio/wav",
                ".webm": "audio/webm",
                ".m4a": "audio/mp4",
            }.get(ext, "application/octet-stream")
            headers = {"Content-Type": content_type}

            response = await self._client.post(self.whisper_url, content=audio_bytes, headers=headers)
            if response.status_code != 200:
                err = await response.aread()
                return {"text": "", "error": f"[Whisper Error {response.status_code}]: {err.decode('utf-8')}"}

            json_data = response.json()
            return {"text": json_data.get("text", "").strip(), "error": None if json_data.get("text", "").strip() else "Empty transcription"}

        except Exception as e:
            return {"text": "", "error": f"Transcription failed: {str(e)}"}
        finally:
            try:
                if input_path and os.path.exists(input_path):
                    await asyncio.to_thread(os.remove, input_path)
            except Exception:
                pass
