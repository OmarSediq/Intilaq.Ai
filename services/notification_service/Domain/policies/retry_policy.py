
import asyncio


class RetryPolicy:

    def __init__(self, max_attempts: int, dlq):
        self.max_attempts = max_attempts
        self.dlq = dlq

    async def run(self, key: str, action):
        attempts = 0

        while attempts < self.max_attempts:
            try:
                return await action()
            except Exception as exc:
                attempts += 1

                if attempts >= self.max_attempts:
                    if self.dlq:
                        await self.dlq.push(key, exc)
                    raise

                await asyncio.sleep(2 ** attempts)

