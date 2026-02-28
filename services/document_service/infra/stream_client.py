# infra/redis/stream_client.py

import json
from Core.config import settings
from Core.logger import logger
from Domain.contracts.events.event_envelope import EventEnvelope
from utils.date_utils import parse_iso
class RedisStreamClient:

    def __init__(self, redis):
        self.redis = redis
        self.stream = settings.REDIS_STREAM_DOCUMENT
        self.group = settings.REDIS_CONSUMER_GROUP_DOCUMENT
        self.consumer = settings.SERVICE_NAME

    async def ensure_group(self):
        try:
            await self.redis.xgroup_create(
                name=self.stream,
                groupname=self.group,
                id="0",
                mkstream=True,
            )
            logger.info(
                f"Redis consumer group created: stream={self.stream}, group={self.group}"
            )

        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.info("Redis consumer group already exists")
            else:
                logger.exception("Failed to create Redis consumer group")
                raise

        
    async def consume(self):

        # 1️⃣ PEL
        events = await self.redis.xreadgroup(
            groupname=self.group,
            consumername=self.consumer,
            streams={self.stream: "0"},
            count=10,
        )

        for _, messages in events:
            for message_id, payload in messages:
                raw_payload = payload["payload"]
                if isinstance(raw_payload, str):
                    raw_payload = json.loads(raw_payload)

                yield EventEnvelope(
                    event_name=payload["event_name"],
                    version=int(payload["version"]),
                    occurred_at=parse_iso(payload["occurred_at"]),
                    idempotency_key=payload["idempotency_key"],
                    payload=raw_payload,
                    _message_id=message_id,   # 👈 هنا الربط
                )

        # 2️⃣ Live events
        while True:
            events = await self.redis.xreadgroup(
                groupname=self.group,
                consumername=self.consumer,
                streams={self.stream: ">"},
                count=10,
                block=5000,
            )

            for _, messages in events:
                for message_id, payload in messages:
                    raw_payload = payload["payload"]
                    if isinstance(raw_payload, str):
                        raw_payload = json.loads(raw_payload)

                    yield EventEnvelope(
                        event_name=payload["event_name"],
                        version=int(payload["version"]),
                        occurred_at=parse_iso(payload["occurred_at"]),
                        idempotency_key=payload["idempotency_key"],
                        payload=raw_payload,
                        _message_id=message_id,   
                    )



    async def ack(self, envelope: EventEnvelope):
        if not envelope._message_id:
            raise RuntimeError("Cannot ACK event without message_id")

        await self.redis.xack(
            self.stream,
            self.group,
            envelope._message_id,
        )

        

    async def fail(self, message):
        pass
