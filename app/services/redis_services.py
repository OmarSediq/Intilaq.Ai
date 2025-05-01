import aioredis
from fastapi import HTTPException
from typing import Optional, Set

# Create a Redis client using the container address where Redis is running
try:
    redis_client = aioredis.from_url("redis://redis-container:6379", decode_responses=True)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to connect to Redis: {e}")

# ------- Existing Functions (no major change) -------

async def set_code(key: str, code: str, expire_seconds: int = 300):
    try:
        await redis_client.setex(key, expire_seconds, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set code in Redis: {e}")

async def get_code(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get code from Redis: {e}")

async def delete_code(key: str):
    try:
        return await redis_client.delete(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete code from Redis: {e}")

# ------- Modified and New Functions for Sessions -------

# ⛔️ نحذف هذا - لأنه كان يتعامل مع قيمة واحدة
# async def set_user_session_id(user_id: str, session_id: int):
#     await redis_client.set(f"user:{user_id}:session", session_id)

# async def get_user_session_id(user_id: str) -> Optional[int]:
#     session_id = await redis_client.get(f"user:{user_id}:session")
#     return int(session_id) if session_id else None

# ✅ الجديد لدعم multi sessions:

async def add_user_session_id(user_id: str, session_id: int):
    """Add a session ID to the user's set of sessions."""
    try:
        await redis_client.sadd(f"user:{user_id}:sessions", session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add session_id for user in Redis: {e}")

async def get_user_session_ids(user_id: str) -> Set[int]:
    """Get all session IDs for a user."""
    try:
        session_ids = await redis_client.smembers(f"user:{user_id}:sessions")
        return {int(sid) for sid in session_ids} if session_ids else set()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session_ids for user from Redis: {e}")

async def remove_user_session_id(user_id: str, session_id: int):
    """Remove a specific session ID from the user's sessions."""
    try:
        await redis_client.srem(f"user:{user_id}:sessions", session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove session_id for user from Redis: {e}")

# ------- Current Question and Status Functions (no change) -------

async def get_current_question_index(session_id: int) -> int:
    index = await redis_client.get(f"session:{session_id}:current_question")
    return int(index) if index else 0

async def set_current_question_index(session_id: int, index: int):
    await redis_client.set(f"session:{session_id}:current_question", index)

async def add_completed_question(session_id: int, question_index: int):
    await redis_client.sadd(f"session:{session_id}:completed_questions", question_index)

async def get_completed_questions(session_id: int) -> list:
    questions = await redis_client.smembers(f"session:{session_id}:completed_questions")
    return list(map(int, questions)) if questions else []

async def set_session_status(session_id: int, status: str):
    await redis_client.set(f"session:{session_id}:status", status)

async def get_session_status(session_id: int) -> Optional[str]:
    return await redis_client.get(f"session:{session_id}:status")

async def get_user_session_ids(user_id: str) -> set[int]:
    """
    Get all session IDs for a specific user from Redis.

    Args:
        user_id (str): The user's ID.

    Returns:
        Set[int]: A set of session IDs.
    """
    try:
        session_ids = await redis_client.smembers(f"user:{user_id}:sessions")
        return {int(session_id) for session_id in session_ids} if session_ids else set()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session IDs: {str(e)}")
