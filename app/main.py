from fastapi import FastAPI
from app.database.models.base import Base
from app.database.models import cv_section_models, hr_models  # noqa: F401
from app.core.dependencies import postgres_engine
from app.api import all_routers  
from app.utils.exception_handlers import register_exception_handlers
from app.core.middlewares.db_transaction import DBTransactionMiddleware 
from app.core.middlewares.auth_logging import AuthenticationMiddleware
from app.core.middlewares.performance_logging import PerformanceLoggingMiddleware
from app.services.mongo_services import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
import sqlalchemy as sa



async def create_tables():
    try:
        print("Starting table creation...")

        async with postgres_engine.begin() as conn:
            # 1. Create schema if it does not exist
            await conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS hr_section"))

            # 2. Create all tables
            await conn.run_sync(Base.metadata.create_all)

        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Running startup tasks...")
    await create_tables()
    await connect_to_mongo()


    yield

    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(PerformanceLoggingMiddleware)
app.add_middleware(DBTransactionMiddleware)


for router in all_routers:
    app.include_router(router)
