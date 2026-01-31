# from typing import Optional
# from fastapi import Request , Depends
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
# import redis.asyncio as redis
# from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

# from backend.core.config import settings
# from collections.abc import AsyncGenerator

# # _mongo_client: Optional[AsyncIOMotorClient] = None
# # =================== PostgreSQL Configuration ===================
# postgres_engine = create_async_engine(settings.POSTGRES_URL, future=True, echo=True)
# SessionLocal = sessionmaker(bind=postgres_engine, class_=AsyncSession, expire_on_commit=False)

# async def get_db(request: Request) -> AsyncSession:
#     async with SessionLocal() as session:
#         request.state.db = session
#         yield session

# async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         yield session


# # =================== Redis Configuration ===================
# redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# async def get_redis_client() -> redis.Redis:
#     try:
#         await redis_client.ping()
#         print("Redis connection successful.")
#         return redis_client
#     except Exception as e:
#         print(f"Error connecting to Redis: {e}")
#         raise RuntimeError("Redis connection failed")  

# # =================== MongoDB Configuration ===================

# mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
# # mongo_db = mongo_client[settings.MONGO_DB_NAME]

# async def get_mongo_client(request: Request) -> AsyncIOMotorClient:
#     try:
#         await mongo_client.admin.command('ping')
#         request.state.mongo = mongo_client
#         return mongo_client
#     except Exception as e:
#         print(f"Error connecting to MongoDB: {e}")
#         raise RuntimeError("MongoDB connection failed")  

# # def get_mongo_collection(collection_name: str):
# #     return mongo_db[collection_name]

# # async def get_mongo_client_raw() -> AsyncIOMotorClient:
# #     return AsyncIOMotorClient(settings.MONGO_URI)

# def get_gridfs_bucket(
#     client: AsyncIOMotorClient = Depends(get_mongo_client)
# ) -> AsyncIOMotorGridFSBucket:
#     db = client["hr_db"]
#     return AsyncIOMotorGridFSBucket(db)

# # def get_mongo_db() -> AsyncIOMotorDatabase:
# #     return mongo_db

# # =================== MongoDB Startup / Shutdown ===================

# async def connect_to_mongo():
#     try:
#         await mongo_client.admin.command('ping')
#         print("MongoDB connected.")
#     except Exception as e:
#         print(f"Failed to connect to MongoDB: {e}")
#         raise RuntimeError("MongoDB startup failed")

# async def close_mongo_connection():
#     mongo_client.close()
#     print("MongoDB connection closed.")



# _mongo_client: Optional[AsyncIOMotorClient] = None

# def get_mongo_client_raw() -> AsyncIOMotorClient:
#     """Synchronous getter — returns singleton AsyncIOMotorClient."""
#     global _mongo_client
#     if _mongo_client is None:
#         _mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
#     return _mongo_client

# def get_mongo_db(db_name: str = "hr_db") -> AsyncIOMotorDatabase:
#     """Return AsyncIOMotorDatabase for given name (sync)."""
#     client = get_mongo_client_raw()
#     return client[db_name]

# # def get_mongo_client_raw_2() -> AsyncIOMotorClient:
# #     """
# #     Synchronous getter: returns the shared AsyncIOMotorClient instance.
# #     Safe to call from sync __init__ or providers.
# #     """
# #     global _mongo_client
# #     if _mongo_client is None:
# #         _mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
# #     return _mongo_client