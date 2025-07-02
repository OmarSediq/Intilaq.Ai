import whisper
import warnings
import traceback
import torch
import subprocess
import numpy as np
import asyncio

from speech_to_text_service.models.whisper_loader import get_whisper_model

class WhisperTranscriber:
    def __init__(self):
        self.model = get_whisper_model()

    async def transcribe_bytes(self, audio_bytes: bytes) -> dict:
        try:

            audio_array = await asyncio.to_thread(self._convert_bytes_to_array, audio_bytes)

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                result = await asyncio.to_thread(
                    lambda: self._transcribe_with_no_grad(audio_array)
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

    def _convert_bytes_to_array(self, audio_bytes: bytes) -> np.ndarray:
        process = subprocess.Popen(
            ["ffmpeg", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", "16000", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        raw_audio, _ = process.communicate(input=audio_bytes)
        return np.frombuffer(raw_audio, dtype=np.float32)

    def _transcribe_with_no_grad(self, audio_array: np.ndarray):
        with torch.no_grad():
            return self.model.transcribe(audio=audio_array)
