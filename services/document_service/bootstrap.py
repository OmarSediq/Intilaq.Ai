from Application.use_cases.generate_document import GenerateDocumentUseCase
from Application.handlers.document_handler import DocumentHandler
from infra.cache.redis_document_cache import RedisDocumentCache
from infra.rendering.jinja_html_renderer import JinjaHtmlRenderer
from infra.rendering.docx_renderer import DocxRenderer
from infra.stream_client import RedisStreamClient
from infra.rendering.pdf_generator import PdfGenerator
from infra.mongodb import get_mongo_client, get_snapshot_repo, get_document_repo
from redis.asyncio import Redis
from Core.config import settings , TEMPLATES_DIR
from Core.logging_config import configure_logging
from infra.redis_client import get_redis
from Application.mappers.event_mapper import EventMapper
from Domain.policies.retry_policy import RetryPolicy

async def bootstrap():
    configure_logging("document_service")

    # ---- Infra ----

    snapshot_repo = await get_snapshot_repo()
    document_repo = await get_document_repo()

    html_renderer = JinjaHtmlRenderer(template_dir=str(TEMPLATES_DIR))
    pdf_renderer = PdfGenerator()

    docx_renderer = DocxRenderer()


    # redis_client = Redis.from_url(settings.REDIS_URL)

    # cache = RedisDocumentCache(redis_client)
    
    redis = await get_redis()
    stream = RedisStreamClient(redis)
    await stream.ensure_group()
    
    retry_policy = RetryPolicy(
        max_attempts=1,
        dlq=None,
    )

    # ---- Use Case ----
    use_case = GenerateDocumentUseCase(
        snapshot_repo=snapshot_repo,
        html_contract=html_renderer,
        pdf_contract=pdf_renderer,
        docx_contract=docx_renderer,
        document_repo=document_repo,
    )
    # ---- Routes ----

    routes = {
            "document.cv_generation.requested": (
                EventMapper.to_document_request,
                use_case
            )
        }

        # ---- Handler ----

    handler = DocumentHandler(routes=routes , retry_policy=retry_policy)

    return {
        "document_handler": handler,
        "stream": stream,
    }

  