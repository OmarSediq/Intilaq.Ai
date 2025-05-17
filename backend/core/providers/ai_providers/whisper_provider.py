from fastapi import Depends
from backend.domain_services.ai_services.whisper_transcriber_service import WhisperTranscriberService

def get_whisper_transcriber_service(_: None = Depends()) -> WhisperTranscriberService:
    return WhisperTranscriberService()
