from Application.use_cases.generate_document import GenerateDocumentUseCase
from Application.handlers.document_handler import DocumentHandler
from infra.mongo import get_snapshot_repo
from infra.stream_client import RedisStreamClient
from Core.logging_config import configure_logging


async def bootstrap():
    configure_logging("document_service")

    # infra
    snapshot_repo = await get_snapshot_repo()
    stream = RedisStreamClient()

    # use case
    use_case = GenerateDocumentUseCase(
        snapshot_repo=snapshot_repo,
    )

    handler = DocumentHandler(
        use_case=use_case,
        stream=stream,
    )

    return handler
