from abc import ABC , abstractmethod

class DocumentCache(ABC):
    @abstractmethod
    async def store_html (self , snapshot_id : str  , html : str )-> None:
        pass 


    @abstractmethod   
    async def get_html (self , snapshot_id : str )-> str | None:
        pass 