import asyncio
from fastapi import FastAPI
from app.models import Base
from app.dependencies import postgres_engine
from app.routers.auth import router as app_router
from app.routers.cvs import router as cv_router
from app.services.mongo_services import mongo_client 
from app.config import env
from app.middlewares import setup_cors


app = FastAPI()
setup_cors(app)
# Add application routes
app.include_router(app_router)
app.include_router(cv_router)

async def create_tables():
    """
    Create all tables defined in the models.
    """
    try:
        print("Starting table creation...")
        async with postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")



@app.on_event("startup")
async def on_startup():
    """
    Run tasks during application startup.
    """
    print("Running startup tasks...")
    await create_tables()


@app.on_event("shutdown")
async def on_shutdown():
    """
    Run tasks during application shutdown.
    """
    print("Closing MongoDB connection...")
    mongo_client.close()
    print("MongoDB connection closed.")

