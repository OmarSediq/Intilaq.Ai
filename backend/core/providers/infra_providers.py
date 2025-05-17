from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from backend.core.config import settings

# =================== PostgreSQL Configuration ===================
postgres_engine = create_async_engine(settings.POSTGRES_URL, future=True, echo=True)
SessionLocal = sessionmaker(bind=postgres_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db(request: Request) -> AsyncSession:
    async with SessionLocal() as session:
        request.state.db = session
        yield session

# =================== Redis Configuration ===================
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis_client() -> redis.Redis:
    try:
        await redis_client.ping()
        print("Redis connection successful.")
        return redis_client
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        raise RuntimeError("Redis connection failed")  

# =================== MongoDB Configuration ===================

mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

async def get_mongo_client(request: Request) -> AsyncIOMotorClient:
    try:
        await mongo_client.admin.command('ping')
        request.state.mongo = mongo_client
        return mongo_client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise RuntimeError("MongoDB connection failed")  

def get_mongo_collection(collection_name: str):
    return mongo_db[collection_name]


# =================== MongoDB Startup / Shutdown ===================

async def connect_to_mongo():
    try:
        await mongo_client.admin.command('ping')
        print("MongoDB connected.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError("MongoDB startup failed")

async def close_mongo_connection():
    mongo_client.close()
    print("MongoDB connection closed.")
