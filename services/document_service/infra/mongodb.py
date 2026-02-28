from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from Core.config import settings

_client = None


async def get_mongo_client():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI)
        await _client.admin.command("ping")
        print("Mongo connected successfully")
    return _client


async def get_snapshot_repo():
    client = await get_mongo_client()
    db = client[settings.MONGO_DB_NAME]
    from infra.mongo.cv_snapshot_repository import MongoCvSnapshotRepository
    return MongoCvSnapshotRepository(db)


async def get_document_repo():
    client = await get_mongo_client()
    db = client[settings.MONGO_DB_NAME]
    bucket = AsyncIOMotorGridFSBucket(db)
    from infra.mongo.document_repository import MongoDocumentRepository
    return MongoDocumentRepository(bucket)
