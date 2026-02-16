# consumer.py

from Core.logger import logger

async def run_consumer(handler, stream):
    logger.info("Notification consumer started")

    async for message in stream.consume():
        try:
            await handler.handle(message)
            await stream.ack(message)
        except Exception:
            logger.exception("notification.failed")
            await stream.fail(message)
