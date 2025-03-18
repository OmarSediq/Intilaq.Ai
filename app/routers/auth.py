from fastapi import APIRouter, HTTPException, Depends,Request,Response
from app.services.db_services import create_user, get_user_by_username, verify_reset_code, save_reset_code, get_user_by_email, update_verification_status, update_user_details, delete_user_by_id,get_user_by_id,get_email_by_code
# from app.utils.jwt_utils import create_access_token, decode_access_token
from app.dependencies import get_db
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import random
from app.utils.email_utils import send_email
# from app.services.redis_services import get_code, set_code, delete_code
from app.utils.jwt_utils import create_access_token,decode_access_token,delete_refresh_token,store_refresh_token,create_refresh_token,get_stored_refresh_token,decode_refresh_token
from fastapi import Depends
from app.utils.response_schemas import success_response,error_response
from datetime import datetime, timezone
import jwt
from fastapi.responses import JSONResponse



router = APIRouter()

async def get_current_user(request: Request):
    access_token = request.cookies.get("access_token") 
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated (No access token)")

    try:
        print(f"Received Token from Cookies: {access_token}")  
        user_data = decode_access_token(access_token)
        print(f"Decoded Token: {user_data}")  

        exp = user_data.get("exp")
        if exp is None:
            raise HTTPException(status_code=401, detail="Invalid token: No expiration found")

        exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)  
        now_time = datetime.now(timezone.utc) 
        print(f"Token Expiration: {exp_time}, Current Time: {now_time}")  

        if exp_time < now_time:
            raise HTTPException(status_code=401, detail="Token has expired")

        return user_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Unexpected Error: {e}")  
        raise HTTPException(status_code=401, detail="Invalid token")
# Models
class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyAccountRequest(BaseModel):
    # email: EmailStr
    code: str

class TwoFactorAuthRequest(BaseModel):
    two_fa_code: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_code: str
    new_password: str

class ResendCodeRequest(BaseModel):
    email: EmailStr
    

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str 

class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str




# OPTIONS for Register
@router.options("/api/users/register/", tags=["Authentication"])
async def options_register():
    return JSONResponse(content=None, headers={
        "Allow": "POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    })

# OPTIONS for Verify Account
@router.options("/api/users/verify-account/", tags=["Security"])
async def options_verify_account():
    return JSONResponse(content=None, headers={
        "Allow": "POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    })

# OPTIONS for Login
@router.options("/api/auth/login/", tags=["Authentication"])
async def options_login():
    return JSONResponse(content=None, headers={
        "Allow": "POST, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    })

@router.post("/api/users/register/", tags=["Authentication"])
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    if request.password != request.confirm_password:
        return error_response(code=400, error_message="Passwords do not match")

    existing_user = await get_user_by_username(request.username, db)
    if existing_user:
        return error_response(code=400, error_message="Username already exists")

    await create_user(request.username, request.password, request.email, db)
    verification_code = str(random.randint(100000, 999999))

    try:
        await save_reset_code(request.email, verification_code, db)
        send_email(request.email, "Verify Your Account", f"Your verification code is: {verification_code}")
    except Exception as e:
        return error_response(code=500, error_message=f"Error during signup: {str(e)}")

    return success_response(code=201, data={"message": "Account created successfully. Please verify your account."})


@router.post("/api/users/verify-account/", tags=["Security"])
async def verify_account(request: VerifyAccountRequest, db: AsyncSession = Depends(get_db)):
    email = await get_email_by_code(request.code, db)
    if not email:
        return error_response(code=400, error_message="Invalid or expired verification code")
    is_valid = await verify_reset_code(email, request.code, db)
    if not is_valid:
        return error_response(code=400, error_message="Invalid or expired verification code")

    await update_verification_status(email, db)

    return success_response(code=200, data={"message": "Account verification successful."})


@router.post("/api/auth/login/", tags=["Authentication"])
async def login(request: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)
    if not user or not user.verify_password(request.password):
        return error_response(code=401, error_message="Invalid credentials")

    if not user.is_verified:
        return error_response(code=403, error_message="Account not verified")

    access_token = create_access_token(user_id=str(user.id), role="regular_user")
    refresh_token = create_refresh_token(user_id=str(user.id))

    await store_refresh_token(str(user.id), refresh_token)  

    response = success_response(code=200, data={"message": "Login successful"})

   
    response.set_cookie("access_token", access_token, httponly=True, samesite="Lax", max_age=900, secure=False, path="/")
    response.set_cookie("refresh_token", refresh_token, httponly=True, samesite="Lax", max_age=604800, secure=False, path="/")

    return response


@router.post("/api/auth/logout/", tags=["Authentication"])
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token") 

    if not refresh_token:
        return error_response(code=401, error_message="No Refresh Token found")

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = payload["user_id"]

        stored_refresh_token = await get_stored_refresh_token(user_id)
        if stored_refresh_token != refresh_token:
            return error_response(code=401, error_message="Invalid Refresh Token")

        await delete_refresh_token(user_id)
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return success_response(code=200, data={"message": "Logout successful"})

    except jwt.ExpiredSignatureError:
        return error_response(code=401, error_message="Refresh Token expired")
    except jwt.InvalidTokenError:
        return error_response(code=401, error_message="Invalid Refresh Token")
    

@router.post("/api/auth/refresh-token/", tags=["Authentication"])
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")  # استخراج `Refresh Token` من `Cookies`

    if not refresh_token:
        return error_response(code=401, error_message="Refresh token not found")

    try:
        payload = decode_refresh_token(refresh_token)  # فك تشفير `Refresh Token`
        user_id = payload["user_id"]

        stored_refresh_token = await get_stored_refresh_token(user_id) 
        if stored_refresh_token != refresh_token:
            return error_response(code=401, error_message="Invalid Refresh Token")

        new_access_token = create_access_token(user_id=user_id, role="regular_user")

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            samesite="Lax",
            max_age=900,  
            secure=False,
            path="/"
        )

        return success_response(code=200, data={"message": "Token refreshed"})

    except jwt.ExpiredSignatureError:
        return error_response(code=401, error_message="Refresh Token expired")
    except jwt.InvalidTokenError:
        return error_response(code=401, error_message="Invalid Refresh Token")

@router.get("/api/users/{user_id}/", tags=["User Management"])
async def get_user_endpoint(user_id: int, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if int(user["user_id"]) != user_id: 
        return error_response(code=403, error_message="You can only access your own data.")

    user_data = await get_user_by_id(user_id, db)
    if not user_data:
        return error_response(code=404, error_message="User not found")

    return success_response(code=200, data={"id": user_data.id, "username": user_data.username, "email": user_data.email})


@router.put("/api/users/update/", tags=["User Management"])
async def update_user_endpoint(request: UpdateUserRequest, user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = int(user["user_id"])  

    updated_user = await update_user_details(user_id, request.model_dump(), db)
    if not updated_user:
        return error_response(code=404, error_message="User not found")

    return success_response(code=200, data={"username": updated_user.username, "email": updated_user.email})


@router.delete("/api/users/delete/", tags=["User Management"])
async def delete_user_endpoint(user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = int(user["user_id"])  

    deletion_status = await delete_user_by_id(user_id, db)
    if not deletion_status:
        return error_response(code=404, error_message="User not found")

    return success_response(code=200, data={"message": "Account deleted successfully"})


@router.post("/api/security/forgot-password/", tags=["Security"])
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)
    if not user:
        return error_response(code=404, error_message="Email not registered")
    
    reset_code = str(random.randint(100000, 999999))
    await save_reset_code(request.email, reset_code, db)
    
    try:
        send_email(request.email, "Reset Your Password", f"Your reset code is: {reset_code}")
    except Exception as e:
        return error_response(code=500, error_message=f"Failed to send email: {str(e)}")
    
    return success_response(code=200, data={"message": "Reset code sent to your email"})


@router.post("/api/users/resend-verification-code/", tags=["Security"])
async def resend_verification_code(request: ResendCodeRequest, db: AsyncSession = Depends(get_db)):

    user = await get_user_by_email(request.email, db)
    
    if not user:
        return error_response(code=404, error_message="User not found")

    if user.is_verified:
        return error_response(code=400, error_message="Account already verified")

    new_code = str(random.randint(100000, 999999))

    await save_reset_code(request.email, new_code, db)

    try:
        send_email(user.email, "Resend Verification Code", f"Your new verification code is: {new_code}")
    except Exception as e:
        return error_response(code=500, error_message=f"Failed to send email: {str(e)}")

    return success_response(code=200, data={"message": "Verification code resent successfully"})
