import asyncio

from bootstrap import bootstrap
from consumer import run_consumer


async def main():
    container = await bootstrap()
   
    await run_consumer(
        handler=container["document_handler"],
        stream=container["stream"],
    )

if __name__ == "__main__":
    asyncio.run(main())
