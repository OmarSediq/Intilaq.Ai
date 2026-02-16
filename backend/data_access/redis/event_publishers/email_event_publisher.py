import json
from redis.asyncio import Redis
from backend.core.base_service import TraceableService
from backend.core.contracts.publishers.email_event_publisher import EmailEventPublisher
from backend.core.providers.redis_provider import stream_xadd
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.core.config import settings

class RedisEmailEventPublisher(EmailEventPublisher, TraceableService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def publish(self, event: EventEnvelope) -> None:
        await stream_xadd(
            redis=self.redis,
            stream_name=settings.redis_stream_notification,
            payload={
                "event_name": event.event_name,
                "version": event.version,
                "occurred_at": event.occurred_at.isoformat(),
                "idempotency_key": event.idempotency_key,
                "payload": json.dumps(event.payload),

        },
    )

