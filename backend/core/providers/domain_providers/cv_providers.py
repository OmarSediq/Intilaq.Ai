from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.containers import repositories_container
# from backend.core.providers.data_access_providers.cv_providers.header_repository_provider import get_header_repository
# from backend.core.providers.data_access_providers.cv_providers.resume_repository_provider import get_resume_repository
# from backend.core.providers.data_access_providers.doc_providers.doc_providers import get_resume_html_renderer 
# from backend.core.providers.data_access_providers.doc_providers.gridfs_repository_provider import get_gridfs_storage
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.domain_services.cv_services.cv_objective_service import CVHeaderRepository , CVObjectiveRepository
from backend.domain_services.cv_services.cv_experience_service import CVExperienceService 
from backend.domain_services.cv_services.cv_education_service import CVEducationService
from backend.domain_services.cv_services.cv_project_service import CVProjectService 
from backend.domain_services.cv_services.cv_skill_language_service import CVSkillsService 
from backend.domain_services.cv_services.cv_certification_service import CVCertificationService 
from backend.domain_services.cv_services.cv_volunteering_service import CVVolunteeringService 
from backend.domain_services.cv_services.cv_award_service import CVAwardService 
# from backend.domain_services.cv_services.cv_resume_export_service import CVResumeExportService , ResumeRepository , ResumeHTMLRenderer , PDFGeneratorService , DocxGenerator , GridFSStorageService
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.containers.application_container import ApplicationContainer
from dependency_injector.wiring import inject , Provide
from backend.core.containers.ai_container import AIContainer

@inject
def get_cv_header_service (
    db : AsyncSession = Depends (provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory])
): 
    header_repo = header_repo_factory(db)
    return CVHeaderRepository(db=db , header_repo = header_repo)

@inject
def get_cv_objective_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    objective_repo_factory = Depends(Provide[ApplicationContainer.repos.objective_repository_factory]),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory]),
    gemini_service = Depends(Provide[ApplicationContainer.service.gemini_service])
) : 
    objective_repo = objective_repo_factory(db)
    header_repo = header_repo_factory(db)
    return CVObjectiveRepository(db=db , objective_repo=objective_repo , header_repo=header_repo,gemini_service=gemini_service)

@inject
def get_cv_experience_service(
    db:AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory =Provide[RepositoriesContainer.header_repository_factory],
    experience_repo_factory =Provide[RepositoriesContainer.experience_repository_factory],
    gemini_service =Provide[AIContainer.gemini_service]
):
    header_repo = header_repo_factory(db)
    experience_repo=experience_repo_factory(db)
    return CVExperienceService(db=db , header_repo=header_repo , experience_repo=experience_repo , gemini_service=gemini_service)

@inject
def get_cv_education_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    education_repo_factory = Provide[repositories_container.EducationRepository]
):
    header_repo = header_repo_factory(db)
    education_repo = education_repo_factory(db)
    return CVEducationService(db=db , header_repo=header_repo,education_repo=education_repo)

@inject
def get_cv_project_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    project_repo_factory = Provide[RepositoriesContainer.project_repository_factory],
    gemini_service = Provide[AIContainer.gemini_service]
): 
    header_repo = header_repo_factory(db)
    project_repo = project_repo_factory(db)
    return CVProjectService(db=db , header_repo=header_repo , project_repo=project_repo , gemini_service=gemini_service)

@inject
def get_cv_skills_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    skill_repo_factory = Provide [RepositoriesContainer.skill_language_repository_factory],
    gemini_service = Provide[AIContainer.gemini_service]
): 
    header_repo = header_repo_factory(db)
    skill_repo = skill_repo_factory(db)
    return CVSkillsService(db=db,header_repo=header_repo,skill_repo=skill_repo,gemini_service=gemini_service)


@inject
def get_cv_certification_service(
    db:AsyncSession= Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    cert_repo_factory = Provide[RepositoriesContainer.certification_repository_factory]
):
    header_repo = header_repo_factory(db)
    cert_repo = cert_repo_factory(db)
    return CVCertificationService(db=db , header_repo=header_repo , cert_repo=cert_repo)



@inject
def get_cv_volunteering_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    volunteer_repo_factory = Provide[RepositoriesContainer.volunteering_repository_factory],
    gemini_service = Provide[AIContainer.gemini_service]
):
    header_repo = header_repo_factory(db)
    volunteer_repo = volunteer_repo_factory(db)
    return CVVolunteeringService(db=db , header_repo=header_repo , volunteer_repo=volunteer_repo , gemini_service=gemini_service)


@inject
def get_cv_award_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
    award_repo_factory = Provide[RepositoriesContainer.award_repository_factory]
):
    header_repo = header_repo_factory(db)
    award_repo = award_repo_factory(db)
    return CVAwardService(db=db , header_repo=header_repo , award_repo=award_repo)


# archive this next time (because i need to add all of generate (PDF,DOCS,HTML) to microservice)
# def get_resume_export_service(
#     db: AsyncSession = Depends(get_db),
#     header_repo : CVHeaderRepository = Depends (get_header_repository),
#     resume_repo : ResumeRepository = Depends(get_resume_repository),
#     html_renderer : ResumeHTMLRenderer = Depends(get_resume_html_renderer),
#     gridfs_storage : GridFSStorageService = Depends(get_gridfs_storage)
# )-> CVResumeExportService:
#     return CVResumeExportService( db_sql=db, header_repo=header_repo , resume_repo= resume_repo , html_renderer=html_renderer ,gridfs_storage=gridfs_storage)


# @inject 
# def get_resume_export_service(
#     db : AsyncSession = Depends(provide_request_postgres_session),
#     header_repo_factory = Provide[RepositoriesContainer.header_repository_factory],
#     resume_repo_factory = Provide[RepositoriesContainer.resume_repository_factory],
#     html_renderer_factory = Provide[ServicesContainer.resume_html_renderer],
#     gridfs_storage = Provide[RepositoriesContainer.gridfs_storage_repository_factory]
# )-> CVResumeExportService:
     