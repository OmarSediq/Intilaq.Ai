# backend/core/providers/ai_providers.py
from dependency_injector.wiring import Provide, inject
from backend.core.containers.ai_container import AIContainer
from backend.domain_services.ai_services.whisper_transcriber_service import WhisperTranscriberService
from backend.domain_services.ai_services.whisper_sender_service import WhisperSenderService

@inject
def get_whisper_transcriber_service(
    factory = Provide[AIContainer.whisper_transcriber],
) -> WhisperTranscriberService:
    return factory() 

@inject
def get_whisper_sender_service(
    factory = Provide[AIContainer.whisper_sender],
) -> WhisperSenderService:
    return factory()
