from fastapi import Depends
from motor.motor_asyncio import  AsyncIOMotorDatabase
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from dependency_injector.wiring import Provide , inject
from backend.core.containers.repositories_container import RepositoriesContainer

# def get_hr_invitation_repository(
#     mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
# ) -> HRInvitationRepository:
#     return HRInvitationRepository(mongo_client)
@inject
def get_hr_invitation_repository (
    db : AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    factory = Provide[RepositoriesContainer.hr_invitation_repository_factory]
)-> HRInvitationRepository : 
    return factory(db)