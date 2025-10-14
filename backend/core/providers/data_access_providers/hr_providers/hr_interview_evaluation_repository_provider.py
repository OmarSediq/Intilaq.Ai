from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.providers.infra_providers import get_mongo_client_raw  # تأكد من المسار الصحيح
from backend.data_access.mongo.hr.hr_interview_evaluation_repository import HRInterviewEvaluationRepository

def get_hr_interview_evaluation_repository(
    client: AsyncIOMotorClient = Depends(get_mongo_client_raw),
) -> HRInterviewEvaluationRepository:
    db = client["hr_db"]
    return HRInterviewEvaluationRepository(db)
