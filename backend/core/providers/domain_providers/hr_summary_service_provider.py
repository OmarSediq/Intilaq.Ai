from backend.domain_services.hr_services.hr_summary_service import HRUserSummaryService
from backend.data_access.mongo.hr.hr_interview_client_repository import HRAnswerRepository
from backend.core.providers.infra_providers import get_mongo_client_raw , get_mongo_db
from backend.data_access.mongo.hr.hr_interview_repository import HRInterviewRepository
from backend.data_access.mongo.hr.hr_summary_repository import HRSummaryRepository

async def get_hr_summary_service() -> HRUserSummaryService:
    db = get_mongo_db() 
    answer_repo    = HRAnswerRepository(db)
    interview_repo = HRInterviewRepository(db)
    summary_repo   = HRSummaryRepository(db)
    return HRUserSummaryService(
        answer_repo=answer_repo,
        interview_repo=interview_repo,
        summary_repo=summary_repo
    )
