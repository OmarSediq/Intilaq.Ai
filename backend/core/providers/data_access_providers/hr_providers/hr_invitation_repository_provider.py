from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository

def get_hr_invitation_repository(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> HRInvitationRepository:
    return HRInvitationRepository(mongo_client)
