from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.core.bootstrap.di_setup import make_container
from backend.core.providers.domain_providers import auth_providers, cv_providers, home_providers, hr_providers, hr_summary_service_provider, interview_providers, refresh_token_provider, token_provider, user_provider
from backend.core.providers.domain_providers.auth_providers import get_auth_service
from backend.core.providers.data_access_providers import cv_providers as data_cv_providers, task_providers
from backend.core.providers.data_access_providers import home_providers as data_home_providers
from backend.core.providers.data_access_providers import hr_providers as data_hr_providers
from backend.core.providers.data_access_providers import interview_providers as data_interview_providers
from backend.core.providers.data_access_providers import session_providers 
from backend.utils.exception_handlers import register_exception_handlers
from backend.core.middlewares.db_transaction import DBTransactionMiddleware
from backend.core.middlewares.auth_logging import AuthenticationMiddleware
from backend.core.middlewares.performance_logging import PerformanceLoggingMiddleware
from backend.database.models import cv_models, hr_models  # noqa: F401
# from backend.core.providers.infra_providers import connect_to_mongo, close_mongo_connection
from backend.database.models.base import Base
import sqlalchemy as sa


async def create_tables(container):
    engine = container.infra.sqlalchemy_engine()
    async with engine.begin() as conn:
        await conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS hr_section"))
        await conn.run_sync(Base.metadata.create_all)               



@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.container
    await container.init_resources()
    app.state.session_factory = container.infra.async_session_factory()


    await create_tables(container)
    
    try:
        yield
    finally:

         await container.shutdown_resources()
   


def create_app() -> FastAPI:
    container = make_container()
    container.wire(modules = [auth_providers ,
                              cv_providers , 
                              home_providers , hr_providers 
                               ,hr_summary_service_provider ,
                                interview_providers , 
                                 token_provider ,
                                  user_provider ,
                                  data_cv_providers ,
                                  data_home_providers,
                                  data_hr_providers,
                                  data_interview_providers ,
                                session_providers,
                                task_providers,
                                refresh_token_provider

                                  
                                    ])

    app = FastAPI(lifespan=lifespan)
    app.state.container = container


    from backend.api.cv_api import all_routers as cv_routers
    from backend.api.auth_api.auth import all_routers as auth_routers
    from backend.api.auth_api.auth_hr import all_routers as hr_auth_routers
    from backend.api.home_api import all_routers as home_routers
    from backend.api.interview_api import all_routers as interview_routers
    # from backend.api.hr_interview_api import all_routers as hr_routers


    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(PerformanceLoggingMiddleware)
    app.add_middleware(DBTransactionMiddleware)

    for router_group in [
        cv_routers,
        auth_routers,
        home_routers,
        interview_routers,
        hr_auth_routers,
        # hr_routers,
    ]:
        for router in router_group:
            app.include_router(router)

    register_exception_handlers(app)
        
    return app
