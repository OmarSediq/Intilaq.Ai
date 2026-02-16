from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from backend.utils.response_schemas import success_response, error_response
from backend.utils.password_utils import verify_password
from backend.data_access.postgres.hr.hr_auth_repository import HRRepository
from backend.domain_services.token_services.token_service import TokenService
from backend.domain_services.token_services.refresh_token_service import RefreshTokenService

class HRAuthService:
    def __init__(self, db: AsyncSession , hr_repo :HRRepository , token_service : TokenService  , refresh_token_service : RefreshTokenService):
        self.db = db
        self.hr_repo = hr_repo
        self.token_service = token_service
        self.refresh_token_service = refresh_token_service

    async def login(self, request, response: Response):
        hr_user = await self.hr_repo.get_by_email(request.business_email)
        if not hr_user or not verify_password(request.password, hr_user.hashed_password):
            return error_response(code=401, error_message="Invalid credentials")

        if not hr_user.is_verified:
            return error_response(code=403, error_message="Account not verified")

        access_token = self.token_service.create_access_token(user_id=str(hr_user.id), role="hr")
        refresh_token = self.token_service.create_refresh_token(user_id=str(hr_user.id))
        await self.refresh_token_service.store_refresh_token(str(hr_user.id), refresh_token)

        response = success_response(code=200, data={"message": "Login successful"})
        response.set_cookie("access_token", access_token, httponly=True, samesite="None", max_age=999999999999999999, secure=True, path="/")
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="None", max_age=999999999999999999, secure=True, path="/")
        return response
