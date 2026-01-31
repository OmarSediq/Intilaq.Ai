from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService
from dependency_injector import containers, providers, resources
import httpx
from typing import Optional

class HTTPXClientResource(resources.AsyncResource):

    async def init(
        self,
        base_url: Optional[str] = None,
        timeout: float = 120.0,
        limits: Optional[dict] = None,
    ) -> httpx.AsyncClient:
        """
        This method is called by Dependency Injector.
        All parameters are injected via providers.Resource(...)
        """

        limits = limits or {
            "max_connections": 100,
            "max_keepalive_connections": 20,
        }

        client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(float(timeout)),
            limits=httpx.Limits(**limits),
            transport=httpx.AsyncHTTPTransport(retries=2),
        )

        return client

    async def shutdown(self, client: httpx.AsyncClient) -> None:
        await client.aclose()


class AIContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    httpx_client = providers.Resource(
        HTTPXClientResource,
        base_url=config.ai.whisper.url,
        timeout=config.ai.http_timeout,
        limits={
            "max_connections": config.ai.max_connections,
        },
    )

    whisper_sender = providers.Factory(
        lambda client, url: __import__(
            "backend.domain_services.ai_services.whisper_sender_service",
            fromlist=["WhisperSenderService"],
        ).WhisperSenderService(client, url),
        client=httpx_client,
        url=config.ai.whisper.url,
    )

    whisper_transcriber = providers.Factory(
        lambda client, url: __import__(
            "backend.domain_services.ai_services.whisper_transcriber_service",
            fromlist=["WhisperTranscriberService"],
        ).WhisperTranscriberService(client, url),
        client=httpx_client,
        url=config.ai.whisper.url,
    )

    gemini_service = providers.Singleton(
        GeminiAIService,
        api_key=config.gemini.api_key,
    )
    # whisper_service_Transcriber = providers.Singleton(WhisperTranscriberService, model_path=config.whisper.model_path)


wiring_modules = [
    "backend.core.providers.domain_providers.auth_providers",
    "backend.core.providers.domain_providers.cv_providers",
    "backend.core.providers.domain_providers.home_providers",
    "backend.core.providers.domain_providers.hr_providers",
    "backend.core.providers.domain_providers.hr_summary_service_provider",
    "backend.core.providers.domain_providers.interview_providers",
    "backend.core.providers.domain_providers.token_provider",
    "backend.core.providers.domain_providers.user_provider"

]