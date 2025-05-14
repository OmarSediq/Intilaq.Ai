

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db
from app.services.mongo_services import get_mongo_client

from app.services.cv_services.cv_header_service import CVHeaderService
from app.services.cv_services.cv_objective_service import CVObjectiveService
from app.services.cv_services.cv_experience_service import CVExperienceService
from app.services.cv_services.cv_education_service import CVEducationService
from app.services.cv_services.cv_project_service import CVProjectService
from app.services.cv_services.cv_skill_language_service import CVSkillsService
from app.services.cv_services.cv_certification_service import CVCertificationService
from app.services.cv_services.cv_volunteering_service import CVVolunteeringService
from app.services.cv_services.cv_award_service import CVAwardService
from app.services.cv_services.cv_resume_export_service import CVResumeExportService

# ========== CV ==========
def get_cv_header_service(db: AsyncSession = Depends(get_db)) -> CVHeaderService:
    return CVHeaderService(db)

def get_cv_objective_service(db: AsyncSession = Depends(get_db)) -> CVObjectiveService:
    return CVObjectiveService(db)

def get_cv_experience_service(db: AsyncSession = Depends(get_db)) -> CVExperienceService:
    return CVExperienceService(db)

def get_cv_education_service(db: AsyncSession = Depends(get_db)) -> CVEducationService:
    return CVEducationService(db)

def get_cv_project_service(db: AsyncSession = Depends(get_db)) -> CVProjectService:
    return CVProjectService(db)

def get_cv_skills_service(db: AsyncSession = Depends(get_db)) -> CVSkillsService:
    return CVSkillsService(db)

def get_cv_certification_service(db: AsyncSession = Depends(get_db)) -> CVCertificationService:
    return CVCertificationService(db)

def get_cv_volunteering_service(db: AsyncSession = Depends(get_db)) -> CVVolunteeringService:
    return CVVolunteeringService(db)

def get_cv_award_service(db: AsyncSession = Depends(get_db)) -> CVAwardService:
    return CVAwardService(db)

def get_resume_export_service(
    db: AsyncSession = Depends(get_db),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    return CVResumeExportService(db, mongo_client)
