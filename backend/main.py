from fastapi import FastAPI
from backend.database.models.base import Base
from backend.database.models import cv_models, hr_models  # noqa: F401
from backend.core.providers.infra_providers import postgres_engine
from backend.api.cv_api import all_routers as cv_routers
from backend.api.auth_api.auth import all_routers as auth_routers
from backend.api.auth_api.auth_hr import all_routers as hr_auth_routers
from backend.api.home_api import all_routers as home_routers
from backend.api.interview_api import all_routers as interview_routers
from backend.api.hr_interview_api import all_routers as hr_routers
from backend.utils.exception_handlers import register_exception_handlers
from backend.core.middlewares.db_transaction import DBTransactionMiddleware 
from backend.core.middlewares.auth_logging import AuthenticationMiddleware
from backend.core.middlewares.performance_logging import PerformanceLoggingMiddleware
from backend.core.providers.infra_providers import connect_to_mongo, close_mongo_connection
from contextlib import asynccontextmanager
import sqlalchemy as sa
from fastapi import Depends
from backend.core.providers.domain_providers.token_provider import get_token_service
import os
from dotenv import load_dotenv
load_dotenv()

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

    if os.getenv("ENABLE_REMOTE_DEBUG", "false").lower() == "true":
        try:
            import pydevd_pycharm
            print("[DEBUG] Trying to attach debugger...")
            pydevd_pycharm.settrace(
                'host.docker.internal',
                port=5691,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False
            )
            print("[DEBUG] Debugger attached")
        except Exception as e:
            print(f"[DEBUG] Debug attach failed: {e}")

    await create_tables()
    await connect_to_mongo()

    token_service = await get_token_service()
    app.state.token_service = token_service

    yield

    await close_mongo_connection()

app = FastAPI(lifespan=lifespan)

all_routers = [
    *cv_routers,
    *auth_routers,
    *home_routers,
    *interview_routers,
    *hr_auth_routers,
    *hr_routers,
]

register_exception_handlers(app)
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(PerformanceLoggingMiddleware)
app.add_middleware(DBTransactionMiddleware)

for router in all_routers:
    app.include_router(router)
