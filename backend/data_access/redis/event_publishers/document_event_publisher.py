import json
from backend.core.base_service import TraceableService
from backend.core.contracts.publishers.document_event_publisher import DocumentEventPublisher
from backend.core.providers.redis_provider import stream_xadd
from backend.core.contracts.events.event_envelope import EventEnvelope
from redis.asyncio import Redis
from backend.core.config import settings


class RedisDocumentEventPublisher(DocumentEventPublisher , TraceableService):
    def __init__ (self , redis:Redis):
            self.redis = redis
    async def publish (self , event : EventEnvelope):
          await stream_xadd(
                redis=self.redis ,
                stream_name=settings.redis_stream_document,
                payload={
                "event_name": event.event_name,
                "version": event.version,
                "occurred_at": event.occurred_at.isoformat(),
                "idempotency_key": event.idempotency_key,
                "payload": json.dumps(event.payload),

        },
          )
          
      