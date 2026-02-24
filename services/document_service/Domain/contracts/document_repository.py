from abc import ABC , abstractmethod


class DocumentRepository(ABC):
    @abstractmethod
    async def save (
        self , 
        snapshot_id:str ,
        document_type:str ,
        content: bytes 
    )-> None : 
        pass 
