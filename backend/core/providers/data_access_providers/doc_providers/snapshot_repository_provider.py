
from dependency_injector.wiring import inject , Provide
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.core.dependencies.session.mongo import provide_cv_snapshot_mongo_db
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.data_access.mongo.home.cv_snapshot_repository import CVSnapshotRepository


@inject
def get_snapshot_repository(
    db : AsyncIOMotorDatabase = Depends(provide_cv_snapshot_mongo_db),
    factory = Provide[RepositoriesContainer.snapshot_repository_factory]
)-> CVSnapshotRepository:
     return factory(db)

