from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client_raw
from backend.data_access.mongo.task.tasks_repository import TasksRepository

def get_tasks_repo(db_client: AsyncIOMotorClient = Depends(get_mongo_client_raw)) -> TasksRepository:
    """
    Provider that returns TasksRepository configured to use hr_db.
    Assumes get_mongo_client_raw yields an AsyncIOMotorClient (synchronously via Depends).
    """
    hr_db_name = "hr_db"
    return TasksRepository(db=db_client, db_name=hr_db_name)
