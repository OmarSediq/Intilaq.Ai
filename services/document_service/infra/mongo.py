from shared.mongo.connection import get_mongo_client
from shared.mongo.cv_snapshot_repository import CVSnapshotRepository
from Core.config import settings


async def get_snapshot_repo():
    client = await get_mongo_client(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    return CVSnapshotRepository(db)
