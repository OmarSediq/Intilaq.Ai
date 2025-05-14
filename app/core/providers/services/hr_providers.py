
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db
from app.services.mongo_services import get_mongo_client
from app.services.hr_services.auth_services.hr_auth_service import HRAuthService
from app.services.hr_services.auth_services.hr_register_service import HRRegisterService
from app.services.hr_services.auth_services.hr_verification_service import HRVerificationService
from app.services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
from app.services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService



# ========== HR ==========
def get_hr_auth_service(db: AsyncSession = Depends(get_db)) -> HRAuthService:
    return HRAuthService(db)

def get_hr_register_service(db: AsyncSession = Depends(get_db)) -> HRRegisterService:
    return HRRegisterService(db)

def get_hr_verification_service(db: AsyncSession = Depends(get_db)) -> HRVerificationService:
    return HRVerificationService(db)

async def get_hr_interview_service() -> HRInterviewService:
    client = await get_mongo_client()
    return HRInterviewService(client)

async def get_hr_invitation_service(db: AsyncSession = Depends(get_db)) -> HRInvitationService:
    client = await get_mongo_client()
    return HRInvitationService(client, db)
