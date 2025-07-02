from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.database.models.hr_models import HrUser, ResetCode
from fastapi import HTTPException


class HRRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> HrUser | None:
        """Retrieve an HR user by their business email."""
        result = await self.db.execute(
            select(HrUser).where(HrUser.business_email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, request) -> HrUser:
        """Create a new HR user and hash their password."""
        hr = HrUser(
            name=request.name,
            company_name=request.company_name,
            business_email=request.business_email,
            company_field=request.company_field,
        )
        hr.set_password(request.password)
        self.db.add(hr)
        await self.db.commit()
        await self.db.refresh(hr)
        return hr

    async def save_reset_code(self, email: str, code: str):
        """Save a verification code for the HR user."""
        reset_code = ResetCode(email=email, code=code)
        self.db.add(reset_code)
        await self.db.commit()

    async def verify_reset_code(self, email: str, code: str) -> bool:
        """Verify if the given email and code match an existing record."""
        result = await self.db.execute(
            select(ResetCode).where(
                ResetCode.email == email,
                ResetCode.code == code
            )
        )
        return result.scalar_one_or_none() is not None

    async def update_verification_status(self, email: str):
        """Mark an HR user's account as verified."""
        result = await self.db.execute(
            select(HrUser).where(HrUser.business_email == email)
        )
        hr_user = result.scalar_one_or_none()
        if not hr_user:
            raise HTTPException(status_code=404, detail="HR user not found")
        hr_user.is_verified = 1
        await self.db.commit()
        await self.db.refresh(hr_user)

    async def get_email_by_code(self, code: str) -> str | None:
        """Retrieve email associated with a given HR verification code."""
        result = await self.db.execute(
            select(ResetCode.email).where(ResetCode.code == code)
        )
        return result.scalar_one_or_none()
