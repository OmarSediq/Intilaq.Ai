

from app.data_access.postgres.cv.award_repository import AwardRepository
from app.data_access.postgres.cv.certification_repository import CertificationRepository
from app.data_access.postgres.cv.education_repository import EducationRepository
from app.data_access.postgres.cv.experience_repository import ExperienceRepository
from app.data_access.postgres.cv.header_repository import CVHeaderRepository
from app.data_access.postgres.cv.objective_repository import CVObjectiveRepository
from app.data_access.postgres.cv.project_repository import ProjectRepository
from app.data_access.postgres.cv.skill_language_repository import SkillsLanguagesRepository
from app.data_access.postgres.cv.volunteering_repository import VolunteeringRepository
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db
from app.data_access.mongo.mongo_services import get_mongo_client
from app.domain_services.cv_services.cv_header_service import CVHeaderService
from app.domain_services.cv_services.cv_objective_service import CVObjectiveService
from app.domain_services.cv_services.cv_experience_service import CVExperienceService
from app.domain_services.cv_services.cv_education_service import CVEducationService
from app.domain_services.cv_services.cv_project_service import CVProjectService
from app.domain_services.cv_services.cv_skill_language_service import CVSkillsService
from app.domain_services.cv_services.cv_certification_service import CVCertificationService
from app.domain_services.cv_services.cv_volunteering_service import CVVolunteeringService
from app.domain_services.cv_services.cv_award_service import CVAwardService
from app.domain_services.cv_services.cv_resume_export_service import CVResumeExportService

# ========== CV ==========
def get_cv_header_service(db: AsyncSession = Depends(get_db)) -> CVHeaderService:
    repo = CVHeaderRepository(db)
    return CVHeaderService(repo)

def get_cv_objective_service(db: AsyncSession = Depends(get_db)) -> CVObjectiveService:
    repo = CVObjectiveRepository(db)
    return CVObjectiveService(repo)

def get_cv_experience_service(db: AsyncSession = Depends(get_db)) -> CVExperienceService:
    repo = ExperienceRepository(db)
    return CVExperienceService(repo)

def get_cv_education_service(db: AsyncSession = Depends(get_db)) -> CVEducationService:
    repo = EducationRepository(db)
    return CVEducationService(repo)

def get_cv_project_service(db: AsyncSession = Depends(get_db)) -> CVProjectService:
    repo = ProjectRepository(db)
    return CVProjectService(repo)

def get_cv_skills_service(db: AsyncSession = Depends(get_db)) -> CVSkillsService:
    repo = SkillsLanguagesRepository(db)
    return CVSkillsService(repo)

def get_cv_certification_service(db: AsyncSession = Depends(get_db)) -> CVCertificationService:
    repo = CertificationRepository(db)
    return CVCertificationService(repo)

def get_cv_volunteering_service(db: AsyncSession = Depends(get_db)) -> CVVolunteeringService:
    repo = VolunteeringRepository(db)
    return CVVolunteeringService(repo)

def get_cv_award_service(db: AsyncSession = Depends(get_db)) -> CVAwardService:
    repo = AwardRepository(db)
    return CVAwardService(repo)

def get_resume_export_service(
    db: AsyncSession = Depends(get_db),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    return CVResumeExportService(db, mongo_client)
