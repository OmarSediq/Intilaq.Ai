from fastapi import Depends
from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from backend.core.containers.repositories_container import RepositoriesContainer
from backend.core.dependencies.session.mongo import provide_hr_interview_mongo_db
from dependency_injector.wiring import inject , Provide 
from motor.motor_asyncio import AsyncIOMotorDatabase


def get_hr_summary_service(
    db :AsyncIOMotorDatabase = Depends(provide_hr_interview_mongo_db),
    answer_repo_factory = Depends(Provide[RepositoriesContainer.hr_interview_client_repository_factory]),
    interview_repo_factory = Depends(Provide[RepositoriesContainer.hr_interview_repository_factory]),
    summary_repo_factory = Depends(Provide[RepositoriesContainer.hr_summary_repository_factory] )
)->HRUserSummaryService:
    answer_repo = answer_repo_factory(db)
    interview_repo = interview_repo_factory(db)
    summary_repo = summary_repo_factory(db)

    return HRUserSummaryService(answer_repo=answer_repo , interview_repo=interview_repo , summary_repo=summary_repo)