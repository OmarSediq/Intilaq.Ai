import whisper
import os
import asyncio
import tempfile
import warnings
import traceback
import torch

from speech_to_text_service.models.whisper_loader import get_whisper_model

class WhisperTranscriber:
    def __init__(self):
        self.model = get_whisper_model()

    async def transcribe_bytes(self, audio_bytes: bytes) -> dict:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            tmp.write(audio_bytes)
            temp_path = tmp.name

        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                result = await asyncio.to_thread(
                    lambda: self._transcribe_with_no_grad(temp_path)
                )

                if w:
                    print("[WHISPER WARNING]", "; ".join(str(warn.message) for warn in w))

            transcribed_text = result.get("text", "").strip()
            if not transcribed_text:
                return {
                    "text": "",
                    "error": "[Whisper] Empty transcription or missing 'text' key",
                    "language": result.get("language", "unknown")
                }

            return {
                "text": transcribed_text,
                "language": result.get("language", "unknown"),
                "error": None
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "text": "",
                "error": f"[Whisper] Exception: {str(e)}"
            }

        finally:
            try:
                if os.path.exists(temp_path):
                    await asyncio.to_thread(os.remove, temp_path)
            except Exception as cleanup_err:
                print("[CLEANUP ERROR]", cleanup_err)

    def _transcribe_with_no_grad(self, path):
        with torch.no_grad():
            return self.model.transcribe(audio=path)
