# app/services/whisper_transcriber.py

import whisper
import os
import asyncio
from speech_to_text_service.models.whisper_loader import get_whisper_model
from speech_to_text_service.audio.preprocess_audio import convert_to_wav, clean_audio

class WhisperTranscriber:
    def __init__(self):
        self.model = get_whisper_model()

    async def transcribe(self, original_path: str) -> dict:
        wav_path = await convert_to_wav(original_path)
        cleaned_path = await clean_audio(wav_path)

        audio = await asyncio.to_thread(whisper.load_audio, cleaned_path)
        audio = await asyncio.to_thread(whisper.pad_or_trim, audio)

        lang = "en"

        result = await asyncio.to_thread(self.model.transcribe, cleaned_path)

        await asyncio.to_thread(os.remove, wav_path)
        await asyncio.to_thread(os.remove, cleaned_path)

        return {
            "text": result["text"],
            "language": lang
        }
