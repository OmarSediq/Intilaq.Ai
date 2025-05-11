from fastapi import APIRouter, Depends, Request, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.schemas.hr_schemas.hr_auth import HrSignupRequest, HrLoginRequest, HrVerifyRequest , HrResendCodeRequest
from app.services.hr_services.hr_auth_services import register_hr_user_logic , verify_hr_user_logic,login_hr_user_logic,resend_hr_verification_code_logic

router = APIRouter()

@router.post("/api/hr/register/", tags=["HR Auth"])
async def register_hr(request: HrSignupRequest, db: AsyncSession = Depends(get_db)):
    return await register_hr_user_logic(request, db)


@router.post("/api/hr/verify-account/", tags=["HR Auth"])
async def verify_hr(request: HrVerifyRequest, db: AsyncSession = Depends(get_db)):
    return await verify_hr_user_logic(request.code, db)


@router.post("/api/hr/login/", tags=["HR Auth"])
async def login_hr(request: HrLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    return await login_hr_user_logic(request, response, db)


@router.post("/api/hr/resend-verification-code/", tags=["HR Auth"])
async def resend_code_hr(request: HrResendCodeRequest, db: AsyncSession = Depends(get_db)):
    return await resend_hr_verification_code_logic(request.business_email, db)