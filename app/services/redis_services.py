import aioredis
from fastapi import HTTPException
from typing import Optional


# Create a Redis client using the container address where Redis is running
try:
    redis_client = aioredis.from_url("redis://redis-container:6379", decode_responses=True)
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to connect to Redis: {e}")


async def set_code(key: str, code: str, expire_seconds: int = 300):
    """
    Store a code in Redis with a specified expiration time.

    Args:
        key (str): The unique key to store the code.
        code (str): The code to be stored.
        expire_seconds (int): Expiration time in seconds (default is 5 minutes).
    """
    try:
        await redis_client.setex(key, expire_seconds, code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set code in Redis: {e}")


async def get_code(key: str):
    """
    Retrieve a stored code from Redis.

    Args:
        key (str): The unique key for the code.

    Returns:
        str: The stored code if it exists, otherwise None.
    """
    try:
        return await redis_client.get(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get code from Redis: {e}")


async def delete_code(key: str):
    """
    Delete a code from Redis.

    Args:
        key (str): The unique key for the code.

    Returns:
        int: The number of keys deleted.
    """
    try:
        return await redis_client.delete(key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete code from Redis: {e}")



async def set_user_session_id(user_id: str, session_id: int):
    await redis_client.set(f"user:{user_id}:session", session_id)

async def get_user_session_id(user_id: str) -> Optional[int]:
    session_id = await redis_client.get(f"user:{user_id}:session")
    return int(session_id) if session_id else None

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
