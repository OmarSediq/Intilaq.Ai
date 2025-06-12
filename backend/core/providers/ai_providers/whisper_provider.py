from fastapi import Depends
from backend.domain_services.ai_services.whisper_transcriber_service import WhisperTranscriberService
from backend.domain_services.ai_services.whisper_sender_service import WhisperSenderService

def get_whisper_transcriber_service() -> WhisperTranscriberService:
    return WhisperTranscriberService()

def get_whisper_sender_service() -> WhisperSenderService:
    return WhisperSenderService()
