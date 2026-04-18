# backend/core/containers/infra_container.py
from dependency_injector import containers, providers, resources
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import redis.asyncio as redis
from backend.core.config import Settings

settings = Settings()


class InfraContainer(containers.DeclarativeContainer):
    
    config = providers.Configuration()
    config.postgres.url.from_value(settings.POSTGRES_URL)
    config.mongo.uri.from_value(settings.MONGO_URI)
    config.mongo.db_name.from_value(settings.MONGO_DB_NAME)
    config.redis.url.from_value(settings.REDIS_URL)
    # mongo_client = providers.Resource(MongoResource)

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

    mongo_client = providers.Singleton(
        AsyncIOMotorClient,
        settings.MONGO_URI,
    )


    mongo_hr_db = providers.Singleton(
        lambda client: client["hr_db"],
        client=mongo_client,
    )

    mongo_interview_questions_db = providers.Singleton(
        lambda client: client["questions"],
        client=mongo_client,
    )


    mongo_interview_answers_db = providers.Singleton(
        lambda client: client["answers"],
        client=mongo_client,
    )
    mongo_interview_user_home_summary_db = providers.Singleton(
        lambda client: client["user_home_summary"],
        client=mongo_client,
    )
    
    mongo_interview_session_results_db = providers.Singleton(
        lambda client: client["session_results"],
        client=mongo_client,
    )

    mongo_interview_db = providers.Singleton(
        lambda client: client["interview_db"],
        client=mongo_client,
    )
    mongo_snapshot_db = providers.Singleton(
        lambda client : client["cv_snapshots"] ,
        client = mongo_client
    )
    mongo_resumes_db = providers.Singleton(
        lambda client: client["resumes_db"],
        client=mongo_client,
    )
    mongo_user_cv_state_db = providers.Singleton(
        lambda client: client["user_cv_state"],
        client=mongo_client,
    )
    hr_video_bucket = providers.Singleton(
        AsyncIOMotorGridFSBucket,
        db=mongo_hr_db,
    )

    resumes_bucket = providers.Singleton(
        AsyncIOMotorGridFSBucket,
        db=mongo_resumes_db,
    )

    async def init_gridfs(database):
        return AsyncIOMotorGridFSBucket(database)

    cv_bucket = providers.Resource(
        init_gridfs,
        database=mongo_snapshot_db,
    )

    redis_client = providers.Singleton(
        redis.from_url,
        settings.REDIS_URL,
        decode_responses=True,
    )
