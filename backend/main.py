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
import os
from backend.core.providers.domain_providers.token_provider import get_token_service
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from backend.core.providers.tracing_provider import setup_tracing
from backend.core.instrumentation import instrument_app
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
    # Tracing setup
    enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() in ("1", "true", "yes")
    setup_tracing(service_name="intilaqai-backend", enabled=enable_tracing)
    instrument_app(app, enabled=enable_tracing)

    # DB + Token setup
    await create_tables()
    await connect_to_mongo()
    app.state.token_service = await get_token_service()
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

from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="IntilaqAI - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css",
        init_oauth={},
        swagger_favicon_url="",
    ).update({
        "swaggerOptions": {
            "persistAuthorization": True,
            "withCredentials": True
        }
    })