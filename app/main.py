import asyncio
from fastapi import FastAPI
from app.models import Base
from app.dependencies import postgres_engine
from app.routers.auth import router as app_router
from app.routers.cvs import router as cv_router
from app.routers.interview import router as interview_router
from app.services.mongo_services import connect_to_mongo,close_mongo_connection 
from app.config import env
from app.middlewares import setup_cors


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
    await connect_to_mongo() 

@app.on_event("shutdown")
async def on_shutdown():
    await close_mongo_connection()
    