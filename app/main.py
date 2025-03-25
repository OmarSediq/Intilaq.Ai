import asyncio
from fastapi import FastAPI
from app.database.models import Base
from app.core.dependencies import postgres_engine
from app.api.routes_auth import router as app_router
from app.api.routes_cv import router as cv_router
from app.api.routes_interview import router as interview_router
from app.services.mongo_services import connect_to_mongo,close_mongo_connection 
from app.core.config import env
from app.core.middlewares import setup_cors


app = FastAPI()
setup_cors(app)
# Add application routes
app.include_router(app_router)
app.include_router(cv_router)
app.include_router(interview_router)

async def create_tables():
    try:
        print("Starting table creation...")
        async with postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.on_event("startup")
async def on_startup():
    print("Running startup tasks...")
    await create_tables()
    asyncio.create_task(connect_to_mongo())  

@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()
    