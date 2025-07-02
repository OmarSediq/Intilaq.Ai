from fastapi import Depends
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService
from backend.core.config import settings

def get_gemini_ai_service(
    api_key: str = Depends(lambda: settings.GENAI_API_KEY),
) -> GeminiAIService:
    return GeminiAIService(api_key=api_key)
