import aioredis
from fastapi import HTTPException

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
