from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import delete
from backend.database.models.cv_models import User, ResetCode
from backend.utils.password_utils import get_password_hash
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, username: str, password: str, email: str):
        result = await self.db.execute(
            select(User).filter((User.username == username) | (User.email == email))
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(status_code=400, detail="If the account exists, a code was sent")

        hashed_password = get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password, is_verified=0)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_username(self, username: str):
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def save_reset_code(self, email: str, code: str):
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=5)
        expiration_time = expiration_time.replace(tzinfo=None)

        await self.db.execute(delete(ResetCode).where(ResetCode.email == email))
        self.db.add(ResetCode(email=email, code=code, created_at=expiration_time))

        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def get_email_by_code(self, code: str):
        result = await self.db.execute(select(ResetCode).filter(ResetCode.code == code))
        reset_code = result.scalars().first()
        return reset_code.email if reset_code else None

    async def verify_reset_code(self, email: str, code: str) -> bool:
        result = await self.db.execute(select(ResetCode).filter(ResetCode.email == email, ResetCode.code == code))
        reset_code = result.scalars().first()
        return bool(reset_code and reset_code.created_at > datetime.now(timezone.utc))

    async def update_verification_status(self, email: str):
        user = await self.get_user_by_email(email)
        if user:
            user.is_verified = 1
            try:
                await self.db.commit()
                await self.db.refresh(user)
                return user
            except Exception as e:
                await self.db.rollback()
                raise HTTPException(status_code=500, detail=f"If the account exists, a code was sent {str(e)}")
        raise HTTPException(status_code=404, detail="If the account exists, a code was sent")

    async def update_user_details(self, user_id: int, updated_data: dict):
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="If the account exists, a code was sent")

        for key, value in updated_data.items():
            setattr(user, key, value)

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"If the account exists, a code was sent: {str(e)}")

    async def delete_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="If the account exists, a code was sent")
        await self.db.delete(user)
        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=f"If the account exists, a code was sent: {str(e)}")
        return True

    async def get_user_by_id(self, user_id: int):
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="If the account exists, a code was sent")
        return user
