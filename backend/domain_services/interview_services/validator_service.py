from re import S
from backend.data_access.mongo.interview.interview_repository import InterviewRepository
from backend.data_access.redis.session_redis_repository import SessionRedisRepository

class InterviewValidatorService:
    def __init__(self , repo_interview : InterviewRepository , repo_session : SessionRedisRepository):
        self.repo_interview = repo_interview
        self.repo_session = repo_session

    async def validate_and_sync_session(self, session_id: int, user_id: str) -> bool:
        session = await self.repo_interview.find_session_by_session_id(session_id, user_id)
        if not session:
            return False

        redis_session_ids = await self.repo_session.get_user_session_ids(user_id)

        if session_id not in redis_session_ids:
            await self.repo_session.add_user_session_id(user_id, session_id)

        return True
