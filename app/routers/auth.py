from fastapi import APIRouter, HTTPException, Depends
from app.services.db_services import create_user, get_user_by_username, verify_reset_code, save_reset_code, get_user_by_email, update_verification_status, update_user_details, delete_user_by_id,get_user_by_id
from app.utils.jwt_utils import create_access_token, decode_access_token
from app.dependencies import get_db
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
import random
from app.utils.email_utils import send_email
from app.services.redis_services import get_code, set_code, delete_code

router = APIRouter()

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
    email: EmailStr
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
    code_type: str

class LogoutRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str

# --------------------- Flow 1: Signup, Verify Account, Login, Verify 2FA --------------------- #

@router.post("/api/users/register/", tags=["Authentication"])
async def signup(request: SignupRequest, db: AsyncSession = Depends(get_db)):
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    existing_user = await get_user_by_username(request.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user
    await create_user(request.username, request.password, request.email, db)

    # Generate verification code
    verification_code = str(random.randint(100000, 999999))

    try:
        # Save reset code
        await save_reset_code(request.email, verification_code, db)

        # Send email
        send_email(
            request.email,
            "Verify Your Account",
            f"Your verification code is: {verification_code}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")

    return {"message": "Account created successfully. Please verify your account."}


@router.post("/api/users/verify-account/", tags=["Security"])
async def verify_account(request: VerifyAccountRequest, db: AsyncSession = Depends(get_db)):
    is_valid = await verify_reset_code(request.email, request.code, db)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    await update_verification_status(request.email, db)
    return {"message": "Account verification successful."}

#Endpoint for Login
@router.post("/api/auth/login/", tags=["Authentication"])
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)
    if not user or not user.verify_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified")

    # Generate a 2FA code and store it in Redis
    two_fa_code = str(random.randint(100000, 999999))
    await set_code(f"2fa_code:{user.id}", two_fa_code, expire_seconds=300)

    # Send the 2FA code via email
    try:
        send_email(
            to_email=user.email,
            subject="Your 2FA Code",
            body=f"Your 2FA code is: {two_fa_code}. This code will expire in 5 minutes."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send 2FA email: {str(e)}")

    # Generate an access token for the user
    token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "message": "2FA code sent to your registered email. Please verify."
    }

# Endpoint for 2FA Verification
@router.post("/api/auth/verify-2fa/",tags=["Security"])
async def two_factor_auth(
    request: TwoFactorAuthRequest,  # Body model
    token: dict = Depends(decode_access_token),  # Decode the token to extract user data
    db: AsyncSession = Depends(get_db)
):
    """
    2FA verification endpoint. Validates the code provided by the user.
    """
    # Extract user ID from the token
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=403, detail="Invalid token")

    # Retrieve the stored 2FA code from Redis
    stored_code = await get_code(f"2fa_code:{user_id}")
    if not stored_code or stored_code != request.two_fa_code:
        raise HTTPException(status_code=400, detail="Invalid or expired 2FA code")

    # Delete the 2FA code after successful verification
    await delete_code(f"2fa_code:{user_id}")

    return {"message": "2FA verification successful"}


# --------------------- Reset Password Flow --------------------- #

@router.post("/api/security/forgot-password/",tags=["Security"])
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    reset_code = str(random.randint(100000, 999999))
    await save_reset_code(request.email, reset_code, db)
    send_email(request.email, "Reset Your Password", f"Your reset code is: {reset_code}")
    return {"message": "Reset code sent to your email"}

@router.post("/api/security/reset-password/",tags=["Security"])
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    is_valid = await verify_reset_code(request.email, request.reset_code, db)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired reset code")
    user = await get_user_by_email(request.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.set_password(request.new_password)
    await db.commit()
    return {"message": "Password reset successfully"}

# --------------------- Resend Code --------------------- #
@router.post("/api/users/resend-verification-code",tags=["Security"])
async def resend_code(request: ResendCodeRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(request.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_code = str(random.randint(100000, 999999))

    if request.code_type == "signup":
        await save_reset_code(request.email, new_code, db)
        send_email(user.email, "Resend Signup Verification Code", f"Your new signup verification code is: {new_code}")
        return {"message": "Signup verification code resent to your email"}
    elif request.code_type == "2fa":
        await save_reset_code(request.email, new_code, db)
        send_email(user.email, "Resend 2FA Code", f"Your new 2FA code is: {new_code}")
        return {"message": "2FA code resent to your email"}

    raise HTTPException(status_code=400, detail="Invalid code type")

# --------------------- Logout --------------------- #
@router.post("/api/auth/logout",tags=["Authentication"])
async def logout(request: LogoutRequest, db: AsyncSession = Depends(get_db)):

    user = await get_user_by_email(request.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    email_subject = "Logout Confirmation"
    email_body = f"Hello {user.username},\n\nYou have successfully logged out from your account."
    try:
        send_email(request.email, email_subject, email_body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    return {"message": "Logout successful. A confirmation email has been sent to your email address."}

# --------------------- User Management Endpoints for Frontend --------------------- #

# Read User by ID
@router.get("/api/users/{user_id}/" , tags =["User Management"])
async def get_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to fetch user details by ID.
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"Fetched User: {user.username}, {user.email}")  # Debug
    return {"user": {"id": user.id, "username": user.username, "email": user.email}}

# Update User Details
@router.put("/api/users/{user_id}/update/" , tags=["User Management"])
async def update_user_endpoint(user_id: int, request: UpdateUserRequest, db: AsyncSession = Depends(get_db)):
  
    if request.password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    updated_user = await update_user_details(user_id, request.dict(), db)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    print(f"Updated User: {updated_user.username}")  # Debug

    return {
        "message": "User updated successfully",
        "user": {
            "username": updated_user.username,
            "email": updated_user.email
        }
    }

# Delete User
@router.delete("/api/users/{user_id}/delete/" , tags=["User Management"])
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to delete a user by ID.
    """
    deletion_status = await delete_user_by_id(user_id, db)
    if not deletion_status:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"Deleted User ID: {user_id}")  # Debug
    return {"message": f"User with ID {user_id} deleted successfully"}
