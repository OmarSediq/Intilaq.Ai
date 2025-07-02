import httpx
import os
import tempfile
import asyncio
from backend.core.base_service import TraceableService


class WhisperSenderService(TraceableService):
    def __init__(self, whisper_url: str = None):
        self.whisper_url = whisper_url or os.getenv(
            "WHISPER_SERVICE_URL",
            "http://speech_to_text_service:5001/api/transcribe"
        )

    async def send_audio_for_transcription(
        self, audio_bytes: bytes, filename: str = "audio.webm", mime_type: str = "audio/webm"
    ) -> dict:
        temp_path = None

        try:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                tmp_file.write(audio_bytes)
                temp_path = tmp_file.name


            headers = {"Content-Type": mime_type}

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.whisper_url,
                    content=audio_bytes,
                    headers=headers
                )
                response.raise_for_status()


            data = response.json()
            text = data.get("text", "").strip()

            return {
                "text": text,
                "error": None if text else data.get("error", "Empty transcription")
            }

        except Exception as e:
            return {
                "text": "",
                "error": f"[WhisperSender] Exception: {str(e)}"
            }

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    await asyncio.to_thread(os.remove, temp_path)
                except Exception as cleanup_err:
                    print("[CLEANUP ERROR]", cleanup_err)
