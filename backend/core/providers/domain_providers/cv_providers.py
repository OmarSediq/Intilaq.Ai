from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
# from backend.core.providers.data_access_providers.cv_providers.header_repository_provider import get_header_repository
# from backend.core.providers.data_access_providers.cv_providers.resume_repository_provider import get_resume_repository
# from backend.core.providers.data_access_providers.doc_providers.doc_providers import get_resume_html_renderer 
# from backend.core.providers.data_access_providers.doc_providers.gridfs_repository_provider import get_gridfs_storage
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.domain_services.cv_services.cv_objective_service import CVObjectiveService
from backend.domain_services.cv_services.cv_experience_service import CVExperienceService 
from backend.domain_services.cv_services.cv_header_service import CVHeaderService
from backend.domain_services.cv_services.cv_education_service import CVEducationService
from backend.domain_services.cv_services.cv_project_service import CVProjectService 
from backend.domain_services.cv_services.cv_skill_language_service import CVSkillsService 
from backend.domain_services.cv_services.cv_certification_service import CVCertificationService 
from backend.domain_services.cv_services.cv_volunteering_service import CVVolunteeringService 
from backend.domain_services.cv_services.cv_award_service import CVAwardService 
from backend.domain_services.cv_services.cv_resume_export_service import CVResumeExportService
from backend.core.containers.application_container import ApplicationContainer
from dependency_injector.wiring import inject , Provide

@inject
def get_cv_header_service (
    db : AsyncSession = Depends (provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider])
)-> CVHeaderService: 
    header_repo = header_repo_factory(db)
    return CVHeaderService(db , header_repo)

@inject
def get_cv_objective_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    objective_repo_factory = Depends(Provide[ApplicationContainer.repos.objective_repository_factory.provider]),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service])
) : 
    header_repo = header_repo_factory(db)
    objective_repo = objective_repo_factory(db)
    return CVObjectiveService(db=db , header_repo=header_repo,objective_repo=objective_repo ,gemini_service=gemini_service)

@inject
def get_cv_experience_service(
    db:AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    experience_repo_factory =Depends(Provide[ApplicationContainer.repos.experience_repository_factory.provider]),
    gemini_service =Depends(Provide[ApplicationContainer.ai.gemini_service])
):
    header_repo = header_repo_factory(db)
    experience_repo=experience_repo_factory(db)
    return CVExperienceService(db=db , header_repo=header_repo , experience_repo=experience_repo , gemini_service=gemini_service)

@inject
def get_cv_education_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    education_repo_factory = Depends(Provide[ApplicationContainer.repos.education_repository_factory.provider])
):
    header_repo = header_repo_factory(db)
    education_repo = education_repo_factory(db)
    return CVEducationService(db=db , header_repo=header_repo,education_repo=education_repo)

@inject
def get_cv_project_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    project_repo_factory = Depends(Provide[ApplicationContainer.repos.project_repository_factory.provider]),
    gemini_service =Depends(Provide[ApplicationContainer.ai.gemini_service])
): 
    header_repo = header_repo_factory(db)
    project_repo = project_repo_factory(db)
    return CVProjectService(db=db , header_repo=header_repo , project_repo=project_repo , gemini_service=gemini_service)

@inject
def get_cv_skills_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    skill_repo_factory = Depends(Provide [ApplicationContainer.repos.skill_language_repository_factory.provider]),
    gemini_service =Depends (Provide[ApplicationContainer.ai.gemini_service])
): 
    header_repo = header_repo_factory(db)
    skills_repo = skill_repo_factory(db)
    return CVSkillsService(db=db,header_repo=header_repo,skills_repo=skills_repo,gemini_service=gemini_service)


@inject
def get_cv_certification_service(
    db:AsyncSession= Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    cert_repo_factory = Depends(Provide[ApplicationContainer.repos.certification_repository_factory.provider])
):
    header_repo = header_repo_factory(db)
    cert_repo = cert_repo_factory(db)
    return CVCertificationService(db=db , header_repo=header_repo , cert_repo=cert_repo)



@inject
def get_cv_volunteering_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    volunteer_repo_factory = Depends(Provide[ApplicationContainer.repos.volunteering_repository_factory.provider]),
    gemini_service = Depends(Provide[ApplicationContainer.ai.gemini_service])
):
    header_repo = header_repo_factory(db)
    volunteer_repo = volunteer_repo_factory(db)
    return CVVolunteeringService(db=db , header_repo=header_repo , volunteer_repo=volunteer_repo , gemini_service=gemini_service)


@inject
def get_cv_award_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Depends(Provide[ApplicationContainer.repos.header_repository_factory.provider]),
    award_repo_factory = Depends(Provide[ApplicationContainer.repos.award_repository_factory.provider])
):
    header_repo = header_repo_factory(db)
    award_repo = award_repo_factory(db)
    return CVAwardService(db=db , header_repo=header_repo , award_repo=award_repo)

     
   
@inject 
def get_resume_export_service(
    db : AsyncSession = Depends(provide_request_postgres_session),
    header_repo_factory = Provide[ApplicationContainer.repos.header_repository_factory.provider],
    resume_repo_factory = Provide[ApplicationContainer.repos.resume_repository_factory.provider],
    snapshot_repo_factory = Provide[ApplicationContainer.repos.snapshot_repository_factory.provider],
    snapshot_builder = Provide[ApplicationContainer.service.cv_snapshot_builder_service],
    document_event_publisher = Provide[ApplicationContainer.messaging.document_event_publisher]
):
     header_repo = header_repo_factory(db)
     resume_repo = resume_repo_factory(db)
     snapshot_repo = snapshot_repo_factory()
     return CVResumeExportService (header_repo=header_repo , resume_repo=resume_repo , snapshot_builder=snapshot_builder , snapshot_repo=snapshot_repo , document_event_publisher=document_event_publisher)




# archive this next time (because i need to add all of generate (PDF,DOCS,HTML) to microservice)
# def get_resume_export_service(
#     db: AsyncSession = Depends(get_db),
#     header_repo : CVHeaderRepository = Depends (get_header_repository),
#     resume_repo : ResumeRepository = Depends(get_resume_repository),
#     html_renderer : ResumeHTMLRenderer = Depends(get_resume_html_renderer),
#     gridfs_storage : GridFSStorageService = Depends(get_gridfs_storage)
# )-> CVResumeExportService:
#     return CVResumeExportService( db_sql=db, header_repo=header_repo , resume_repo= resume_repo , html_renderer=html_renderer ,gridfs_storage=gridfs_storage)









