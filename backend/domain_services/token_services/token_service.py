import jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from backend.core.config import settings
from redis.asyncio import Redis

class TokenService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def create_access_token(self, user_id: str, role: str, expiration_minutes: int = 15) -> str:
        expiration = datetime.now(timezone.utc) + timedelta(minutes=expiration_minutes)
        payload = {
            "user_id": user_id,
            "role": role,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int(expiration.timestamp())
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, user_id: str, expiration_days: int = 7) -> str:
        expiration = datetime.now(timezone.utc) + timedelta(days=expiration_days)
        payload = {
            "user_id": user_id,
            "exp": expiration
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    async def store_refresh_token(self, user_id: str, refresh_token: str):
        await self.redis.setex(f"user:{user_id}:refresh_token", 7 * 24 * 3600, refresh_token)

    async def get_stored_refresh_token(self, user_id: str) -> str:
        return await self.redis.get(f"user:{user_id}:refresh_token")

    async def delete_refresh_token(self, user_id: str):
        await self.redis.delete(f"user:{user_id}:refresh_token")

    def decode_access_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def decode_refresh_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Refresh Token")
