

from email import header
from backend.core.providers.ai_providers.gemini_provider import get_gemini_ai_service
from backend.core.providers.data_access_providers.cv_providers.award_repository_provider import get_award_repository
from backend.core.providers.data_access_providers.cv_providers.certification_repository_provider import get_certification_repository
from backend.core.providers.data_access_providers.cv_providers.education_repository_provider import get_education_repository
from backend.core.providers.data_access_providers.cv_providers.experience_repository_provider import get_experience_repository
from backend.core.providers.data_access_providers.cv_providers.header_repository_provider import get_header_repository
from backend.core.providers.data_access_providers.cv_providers.objective_repository_provider import get_objective_repository
from backend.core.providers.data_access_providers.cv_providers.project_repository_provider import get_project_repository
from backend.core.providers.data_access_providers.cv_providers.resume_repository_provider import get_resume_repository
from backend.core.providers.data_access_providers.cv_providers.skill_language_repository_provider import get_skills_languages_repository
from backend.core.providers.data_access_providers.cv_providers.volunteering_repository_provider import get_volunteering_repository
from backend.core.providers.data_access_providers.doc_providers.doc_providers import get_resume_html_renderer , get_docx_generator , get_pdf_generator
from backend.core.providers.data_access_providers.doc_providers.gridfs_repository_provider import get_gridfs_storage
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.providers.infra_providers import get_db
from backend.core.providers.infra_providers import get_mongo_client
from backend.domain_services.cv_services.cv_header_service import CVHeaderService
from backend.domain_services.cv_services.cv_objective_service import CVObjectiveService , GeminiAIService, CVHeaderRepository , CVObjectiveRepository
from backend.domain_services.cv_services.cv_experience_service import CVExperienceService , ExperienceRepository
from backend.domain_services.cv_services.cv_education_service import CVEducationService , EducationRepository
from backend.domain_services.cv_services.cv_project_service import CVProjectService , ProjectRepository
from backend.domain_services.cv_services.cv_skill_language_service import CVSkillsService , SkillsLanguagesRepository
from backend.domain_services.cv_services.cv_certification_service import CVCertificationService , CertificationRepository
from backend.domain_services.cv_services.cv_volunteering_service import CVVolunteeringService , VolunteeringRepository
from backend.domain_services.cv_services.cv_award_service import CVAwardService , AwardRepository
from backend.domain_services.cv_services.cv_resume_export_service import CVResumeExportService , ResumeRepository , ResumeHTMLRenderer , PDFGeneratorService , DocxGenerator , GridFSStorageService

# ========== CV ==========
def get_cv_header_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends(get_header_repository)
    ) -> CVHeaderService:
    return CVHeaderService(db=db , header_repo=header_repo)

def get_cv_objective_service(
    db: AsyncSession = Depends(get_db),
    objective_repo : CVObjectiveRepository = Depends(get_objective_repository),
    header_repo : CVHeaderRepository = Depends(get_header_repository),
    gemini_service : GeminiAIService = Depends(get_gemini_ai_service)
    ) -> CVObjectiveService:
    return CVObjectiveService(db=db , objective_repo=objective_repo , header_repo=header_repo , gemini_service=gemini_service)

def get_cv_experience_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository= Depends(get_header_repository),
    experience_repo : ExperienceRepository = Depends(get_experience_repository),
    gemini_service : GeminiAIService = Depends(get_gemini_ai_service)
        ) -> CVExperienceService:
    return CVExperienceService(db=db, header_repo=header_repo , experience_repo=experience_repo , gemini_service=gemini_service)

def get_cv_education_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository= Depends(get_header_repository),
    education_repo : EducationRepository = Depends(get_education_repository),
        ) -> CVEducationService:
    return CVEducationService(db=db , header_repo=header_repo , education_repo=education_repo)

def get_cv_project_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository= Depends(get_header_repository),
    project_repo : ProjectRepository = Depends(get_project_repository),
    gemini_service : GeminiAIService = Depends(get_gemini_ai_service)
        ) -> CVProjectService:
    return CVProjectService(db=db, header_repo=header_repo , project_repo=project_repo , gemini_service=gemini_service)

def get_cv_skills_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends(get_header_repository),
    skill_repo  : SkillsLanguagesRepository = Depends(get_skills_languages_repository),
    gemini_repo : GeminiAIService = Depends(get_gemini_ai_service)
        ) -> CVSkillsService:
    return CVSkillsService(db=db , header_repo=header_repo , skills_repo=skill_repo , gemini_service=gemini_repo)

def get_cv_certification_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends(get_header_repository),
    cert_repo : CertificationRepository = Depends(get_certification_repository),
        ) -> CVCertificationService:
    return CVCertificationService(db=db,header_repo=header_repo ,cert_repo=cert_repo)

def get_cv_volunteering_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends(get_header_repository),
    volunteer_repo : VolunteeringRepository = Depends(get_volunteering_repository),
    gemini_service : GeminiAIService = Depends(get_gemini_ai_service)
        ) -> CVVolunteeringService:
    return CVVolunteeringService(db=db , header_repo=header_repo , volunteer_repo=volunteer_repo , gemini_service=gemini_service)

def get_cv_award_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends(get_header_repository),
    award_repo : AwardRepository = Depends(get_award_repository),
    ) -> CVAwardService:
    return CVAwardService(db=db , header_repo=header_repo , award_repo=award_repo)

def get_resume_export_service(
    db: AsyncSession = Depends(get_db),
    header_repo : CVHeaderRepository = Depends (get_header_repository),
    resume_repo : ResumeRepository = Depends(get_resume_repository),
    html_renderer : ResumeHTMLRenderer = Depends(get_resume_html_renderer),
    pdf_generator : PDFGeneratorService = Depends(get_pdf_generator),
    docx_generator : DocxGenerator = Depends(get_docx_generator),
    gridfs_storage : GridFSStorageService = Depends(get_gridfs_storage)
)-> CVResumeExportService:
    return CVResumeExportService( db_sql=db, header_repo=header_repo , resume_repo= resume_repo , html_renderer=html_renderer,pdf_generator=pdf_generator,docx_generator=docx_generator,gridfs_storage=gridfs_storage)
