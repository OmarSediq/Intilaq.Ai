from app.data_access.mongo.mongo_services import find_session_by_session_id
from app.data_access.redis.redis_services import get_user_session_ids, add_user_session_id

class InterviewValidatorService:
    async def validate_and_sync_session(self, session_id: int, user_id: str) -> bool:
        session = await find_session_by_session_id(session_id, user_id)
        if not session:
            return False

        redis_session_ids = await get_user_session_ids(user_id)

        if session_id not in redis_session_ids:
            await add_user_session_id(user_id, session_id)

        return True
