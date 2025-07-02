from fastapi import APIRouter, Depends, Request, Response
from backend.core.providers.domain_providers.auth_providers import get_auth_service, get_account_service, get_password_service
from backend.schemas.auth_schema import (
    SignupRequest, VerifyAccountRequest, LoginRequest,
    ForgotPasswordRequest, ResendCodeRequest
)
from backend.domain_services.auth_services.auth_service import AuthService
from backend.domain_services.auth_services.account_service import AccountService
from backend.domain_services.auth_services.password_service import PasswordRecoveryService
from backend.core.providers.domain_providers.user_provider import get_current_user

router = APIRouter()


@router.post("/api/users/register/", tags=["Account"])
async def signup(
    request: SignupRequest,
    service: AccountService = Depends(get_account_service)
):
    return await service.signup(request)


@router.post("/api/users/verify-account/", tags=["Account"])
async def verify_account(
    request: VerifyAccountRequest,
    service: AccountService = Depends(get_account_service)
):
    return await service.verify_account(request)


@router.post("/api/auth/login/", tags=["Account"])
async def login(
    request: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    return await service.login(request, response)


@router.post("/api/auth/logout/", tags=["Account"])
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    return await service.logout(request, response)


@router.post("/api/auth/refresh-token/", tags=["Account"])
async def refresh_token(
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_token(request, response)


@router.post("/api/security/forgot-password/", tags=["Account"])
async def forgot_password(
    request: ForgotPasswordRequest,
    service: PasswordRecoveryService = Depends(get_password_service)
):
    return await service.forgot_password(request)


@router.post("/api/users/resend-verification-code/", tags=["Account"])
async def resend_verification_code(
    request: ResendCodeRequest,
    service: AccountService = Depends(get_account_service)
):
    return await service.resend_verification_code(request)
