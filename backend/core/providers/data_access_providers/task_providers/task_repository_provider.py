from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from backend.data_access.mongo.task.tasks_repository import TasksRepository
from dependency_injector.wiring import inject , Provide


# def get_tasks_repo(db_client: AsyncIOMotorClient = Depends(get_mongo_client_raw)) -> TasksRepository:
#     """
#     Provider that returns TasksRepository configured to use hr_db.
#     Assumes get_mongo_client_raw yields an AsyncIOMotorClient (synchronously via Depends).
#     """
#     hr_db_name = "hr_db"
#     return TasksRepository(db=db_client, db_name=hr_db_name)


@inject 
def get_tasks_repo (
    db : AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    factory = Provide[RepositoriesContainer.tasks_repository_factory]
)-> TasksRepository:
    return factory(db)


