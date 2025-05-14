from pydantic import BaseModel, EmailStr 
from typing import Optional

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyAccountRequest(BaseModel):
    code: str
    new_password: Optional[str] = None  
# class TwoFactorAuthRequest(BaseModel):
#     two_fa_code: str

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

# class LogoutRequest(BaseModel):
#     refresh_token: str 

class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
