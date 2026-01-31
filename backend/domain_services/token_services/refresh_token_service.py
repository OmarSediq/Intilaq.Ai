    
import jwt
from fastapi import HTTPException
from backend.core.config import settings
from redis.asyncio import Redis


class RefreshTokenService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def decode_refresh_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
    async def store_refresh_token(self, user_id: str, refresh_token: str):
        await self.redis.setex(f"user:{user_id}:refresh_token", 7 * 24 * 3600, refresh_token)

    async def get_stored_refresh_token(self, user_id: str) -> str:
        return await self.redis.get(f"user:{user_id}:refresh_token")

    async def delete_refresh_token(self, user_id: str):
        await self.redis.delete(f"user:{user_id}:refresh_token")
