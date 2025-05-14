from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import get_user_by_email
from app.utils.jwt_utils import (
    create_access_token, create_refresh_token, decode_refresh_token,
    store_refresh_token, get_stored_refresh_token, delete_refresh_token
)
from app.utils.response_schemas import success_response, error_response
from app.utils.password_utils import  verify_password
import jwt

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login(self, request, response: Response):
        user = await get_user_by_email(request.email, self.db)
        if not user or not verify_password(request.password, user.hashed_password):
            return error_response(code=401, error_message="Invalid credentials")

        if not user.is_verified:
            return error_response(code=403, error_message="Account not verified")

        access_token = create_access_token(str(user.id), role="regular_user")
        refresh_token = create_refresh_token(str(user.id))
        await store_refresh_token(str(user.id), refresh_token)

        response = success_response(code=200, data={"message": "Login successful"})
        response.set_cookie("access_token", access_token, httponly=True, samesite="None", max_age=604800, secure=True, path="/")
        response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="None", max_age=604800, secure=True, path="/")
        return response

    async def logout(self, request: Request, response: Response):
        token = request.cookies.get("refresh_token")
        if not token:
            return error_response(code=401, error_message="No refresh token found")

        try:
            user_id = decode_refresh_token(token)["user_id"]
            if await get_stored_refresh_token(user_id) != token:
                return error_response(code=401, error_message="Invalid refresh token")
            await delete_refresh_token(user_id)
            response.delete_cookie("access_token", path="/")
            response.delete_cookie("refresh_token", path="/")
            return success_response(code=200, data={"message": "Logout successful"})
        except jwt.ExpiredSignatureError:
            return error_response(code=401, error_message="Token expired")
        except jwt.InvalidTokenError:
            return error_response(code=401, error_message="Invalid token")

    async def refresh_token(self, request: Request, response: Response):
        token = request.cookies.get("refresh_token")
        if not token:
            return error_response(code=401, error_message="No token found")
        try:
            user_id = decode_refresh_token(token)["user_id"]
            if await get_stored_refresh_token(user_id) != token:
                return error_response(code=401, error_message="Invalid refresh token")

            new_token = create_access_token(user_id=user_id, role="regular_user")
            response.set_cookie("access_token", new_token, httponly=True, samesite="Lax", max_age=900, secure=False, path="/")
            return success_response(code=200, data={"message": "Token refreshed"})
        except jwt.ExpiredSignatureError:
            return error_response(code=401, error_message="Token expired")
        except jwt.InvalidTokenError:
            return error_response(code=401, error_message="Invalid token")
