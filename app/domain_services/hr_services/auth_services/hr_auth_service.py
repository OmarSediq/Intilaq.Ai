from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response
from app.data_access.postgres.db_services import get_hr_by_email
from app.utils.jwt_utils import create_access_token, create_refresh_token, store_refresh_token
from app.utils.response_schemas import success_response, error_response
from app.utils.password_utils import verify_password

class HRAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, request, response: Response):
        hr_user = await get_hr_by_email(request.business_email, self.db)
        if not hr_user or not verify_password(request.password, hr_user.hashed_password):
            return error_response(code=401, error_message="Invalid credentials")

        if not hr_user.is_verified:
            return error_response(code=403, error_message="Account not verified")

        access_token = create_access_token(user_id=str(hr_user.id), role="hr")
        refresh_token = create_refresh_token(user_id=str(hr_user.id))
        await store_refresh_token(str(hr_user.id), refresh_token)

        response = success_response(code=200, data={"message": "Login successful"})
        response.set_cookie("access_token", access_token, httponly=True, samesite="None", max_age=604800, secure=True, path="/")
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="None", max_age=604800, secure=True, path="/")
        return response
