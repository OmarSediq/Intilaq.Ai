# backend/core/containers/infra_container.py
from dependency_injector import containers, providers, resources
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import redis.asyncio as redis
from backend.core.config import Settings

settings = Settings()

class MongoResource(resources.AsyncResource):
    async def init(self):
        client = AsyncIOMotorClient(settings.MONGO_URI)
        await client.admin.command("ping")
        print("[INFRA] Mongo connected.")
        return client

    async def shutdown(self, client):
        client.close()
        print("[INFRA] Mongo disconnected.")

class RedisResource(resources.AsyncResource):
    async def init(self):
        client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        await client.ping()
        print("[INFRA] Redis connected.")
        return client

    async def shutdown(self, client):
        try:
            await client.close()
        except Exception:
            pass
        print("[INFRA] Redis disconnected.")


class InfraContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()
    config.postgres.url.from_value(settings.POSTGRES_URL)
    config.mongo.uri.from_value(settings.MONGO_URI)
    config.mongo.db_name.from_value(settings.MONGO_DB_NAME)
    config.redis.url.from_value(settings.REDIS_URL)

    # PostgreSQL
    sqlalchemy_engine = providers.Singleton(
        create_async_engine,
        config.postgres.url,
        future=True,
        echo=False,
    )

    async_session_factory = providers.Factory(
        sessionmaker,
        bind=sqlalchemy_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Mongo
    mongo_client = providers.Resource(MongoResource)
    mongo_db_factory = providers.Factory(
        lambda client, name: client[name],
        client=mongo_client,
        name=config.mongo.db_name
    )
    gridfs_bucket = providers.Factory(lambda db: AsyncIOMotorGridFSBucket(db), db=mongo_db_factory)

    # Redis
    redis_client = providers.Resource(RedisResource)
