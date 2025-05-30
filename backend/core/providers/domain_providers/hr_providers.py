
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service
from backend.core.providers.data_access_providers.hr_providers.hr_answer_repository_provider import \
    get_hr_answer_repository
from backend.core.providers.data_access_providers.hr_providers.hr_auth_repository_provider import get_hr_repository
from backend.core.providers.data_access_providers.hr_providers.hr_invitation_repository_provider import get_hr_invitation_repository
from backend.core.providers.domain_providers.token_provider import get_token_service
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_invitation_repository import HRInvitationRepository
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository
from backend.domain_services.hr_services.client_interview_services.hr_answer_service import HRAnswerService
from backend.domain_services.token_services.token_service import TokenService
from backend.core.providers.data_access_providers.hr_providers.hr_interview_repository_provider import get_hr_interview_repository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.core.providers.infra_providers import get_mongo_client
from backend.domain_services.hr_services.auth_services.hr_auth_service import HRAuthService
from backend.domain_services.hr_services.auth_services.hr_register_service import HRRegisterService
from backend.domain_services.hr_services.auth_services.hr_verification_service import HRVerificationService
from backend.domain_services.hr_services.create_interview_services.hr_interview_service import HRInterviewService
from backend.domain_services.hr_services.create_interview_services.hr_invitation_service import HRInvitationService
from motor.motor_asyncio import AsyncIOMotorClient
from backend.domain_services.ai_services.gemini_ai_service import GeminiAIService


# ========== HR ==========
def get_hr_auth_service(
    db: AsyncSession = Depends(get_db),
    hr_repo : HRRepository = Depends(get_hr_repository),
    token_service : TokenService =Depends(get_token_service)
    ) -> HRAuthService:
    return HRAuthService(db= db , hr_repo=hr_repo , token_service=token_service)

def get_hr_register_service(
    db: AsyncSession = Depends(get_db),
    hr_repo : HRRepository = Depends(get_hr_repository)
        ) -> HRRegisterService:
    return HRRegisterService(db=db , hr_repo=hr_repo)

def get_hr_verification_service(
    db: AsyncSession = Depends(get_db),
    hr_repo : HRRepository = Depends(get_hr_repository)
    ) -> HRVerificationService:
    return HRVerificationService(db=db , hr_repo=hr_repo)


def get_hr_interview_service(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    repository :HRInterviewRepository = Depends(get_hr_interview_repository),
    gemini_service :GeminiAIService = Depends (get_gemini_ai_service)
) -> HRInterviewService: 
    return HRInterviewService(repository=repository,gemini_service=gemini_service)

def get_hr_invitation_service(
    db: AsyncSession = Depends(get_db),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    repo : HRInvitationRepository = Depends (get_hr_invitation_repository)
) -> HRInvitationService:
    return HRInvitationService(repo =repo, db = db)

def get_hr_answer_service(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    answer_repo: HRAnswerRepository = Depends(get_hr_answer_repository),
    invitation_repo: HRInvitationRepository = Depends(get_hr_invitation_repository)
) -> HRAnswerService:
    return HRAnswerService(answer_repo=answer_repo , invitation_repo =invitation_repo)

