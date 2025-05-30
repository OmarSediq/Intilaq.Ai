from fastapi import APIRouter, Depends, Response
from backend.core.providers.domain_providers.hr_providers import get_hr_auth_service , get_hr_register_service , get_hr_verification_service 
from backend.schemas.hr_schemas.hr_auth_schema import HrSignupRequest, HrLoginRequest, HrVerifyRequest , HrResendCodeRequest
from backend.domain_services.hr_services.auth_services.hr_auth_service import HRAuthService
from backend.domain_services.hr_services.auth_services.hr_register_service import HRRegisterService
from backend.domain_services.hr_services.auth_services.hr_verification_service import HRVerificationService 
router = APIRouter()


@router.post("/api/hr/register/", tags=["HR Auth"])
async def register_hr(
    request: HrSignupRequest,
    service: HRRegisterService = Depends(get_hr_register_service)
):
    return await service.register(request)


@router.post("/api/hr/verify-account/", tags=["HR Auth"])
async def verify_hr(
    request: HrVerifyRequest,
    service: HRVerificationService = Depends(get_hr_verification_service)
):
    return await service.verify_code(request.code)


@router.post("/api/hr/login/", tags=["HR Auth"])
async def login_hr(
    request: HrLoginRequest,
    response: Response,
    service: HRAuthService = Depends(get_hr_auth_service)
):
    return await service.login(request, response)


@router.post("/api/hr/resend-verification-code/", tags=["HR Auth"])
async def resend_code_hr(
    request: HrResendCodeRequest,
    service: HRVerificationService = Depends(get_hr_verification_service)
):
    return await service.resend_code(request.business_email)
