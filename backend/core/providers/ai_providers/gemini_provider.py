from dependency_injector.wiring import Provide, inject
from backend.core.containers.ai_container import AIContainer
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService

@inject
def get_gemini_ai_service(
    factory = Provide[AIContainer.gemini_service],
) -> GeminiAIService:
    return factory()  
