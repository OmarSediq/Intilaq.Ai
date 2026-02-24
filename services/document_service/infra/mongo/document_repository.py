from io import BytesIO
from Domain.contracts.document_repository import DocumentRepository


class MongoDocumentRepository(DocumentRepository):
    def __init__ (self ,gridfs_bucket):
        self.bucket = gridfs_bucket

        async def save (
                self , 
                snapshot_id : str ,
                document_type: str ,
                content : bytes
        )-> None:
            
            filename = f"{snapshot_id}.{document_type}"
            await self.bucket.upload_from_stream(
            filename,
            BytesIO(content),
            metadata={
                "snapshot_id": snapshot_id,
                "type": document_type,
            },
        )