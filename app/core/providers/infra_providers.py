from fastapi import Depends, Request
from app.core.config import settings

from app.services.mongo_services import get_mongo_client
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# ========== PostgreSQL Configuration ==========
postgres_engine = create_async_engine(settings.POSTGRES_URL, future=True, echo=True)
SessionLocal = sessionmaker(bind=postgres_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db(request: Request) -> AsyncSession:
    async with SessionLocal() as session:
        request.state.db = session
        yield session

# ========== Redis Configuration ==========
async def get_redis_client():
    try:
        client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
        await client.ping()
        print("Redis connection successful.")
        return client
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return None

# ========== Mongo Collection Access ==========
mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

def get_collection(collection_name: str):
    return mongo_db[collection_name]
