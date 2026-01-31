from backend.core.containers.application_container import ApplicationContainer
from backend.core.config import settings


def make_container() -> ApplicationContainer:
    
    container = ApplicationContainer()
    container.config.from_dict({
        "ai": {
            "http_timeout": 120,
            "max_connections": 100,
            "whisper": {
                "url": settings.WHISPER_SERVICE_URL,
            },
        },
        "gemini": {
            "api_key": settings.GENAI_API_KEY,
        },
        "postgres": {
            "url": settings.POSTGRES_URL,   
        },
        
        "secret_key": settings.SECRET_KEY,
    })

    container.infra.wire()
    container.ai.wire()
    container.repos.wire()
    container.service.wire()
    container.dispatcher.wire()
   

    return container
