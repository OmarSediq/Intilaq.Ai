from typing import Optional, Set
from fastapi import HTTPException
from redis.asyncio import Redis

class SessionRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def add_user_session_id(self, user_id: str, session_id: int):
        try:
            await self.redis.sadd(f"user:{user_id}:sessions", session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add session_id: {e}")

    async def get_user_session_ids(self, user_id: str) -> Set[int]:
        try:
            session_ids = await self.redis.smembers(f"user:{user_id}:sessions")
            return {int(sid) for sid in session_ids} if session_ids else set()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get session_ids: {e}")

    async def remove_user_session_id(self, user_id: str, session_id: int):
        try:
            await self.redis.srem(f"user:{user_id}:sessions", session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove session_id: {e}")

    async def get_current_question_index(self, session_id: int) -> int:
        index = await self.redis.get(f"session:{session_id}:current_question")
        return int(index) if index else 0

    async def set_current_question_index(self, session_id: int, index: int):
        await self.redis.set(f"session:{session_id}:current_question", index)

    async def add_completed_question(self, session_id: int, question_index: int):
        await self.redis.sadd(f"session:{session_id}:completed_questions", question_index)

    async def get_completed_questions(self, session_id: int) -> list[int]:
        questions = await self.redis.smembers(f"session:{session_id}:completed_questions")
        return list(map(int, questions)) if questions else []

    async def set_session_status(self, session_id: int, status: str):
        await self.redis.set(f"session:{session_id}:status", status)

    async def get_session_status(self, session_id: int) -> Optional[str]:
        return await self.redis.get(f"session:{session_id}:status")
