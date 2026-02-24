from Domain.contracts.document_cache import DocumentCache


class RedisDocumentCache(DocumentCache):
    def __init__(self , redis ):
        self.redis = redis 

        async def store_html (self , snapshot_id : str , html :str)-> None: 
            key = f"document:cv:{snapshot_id}:html"
            await self.redis.set(key , html)

        async def get_html (self , snapshot_id : str)-> str|None:
            key = f"document:cv:{snapshot_id}:html"
            return await self.redis.get(key)
