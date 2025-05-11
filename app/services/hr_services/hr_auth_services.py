import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_services import get_hr_by_email, create_hr_user,save_hr_reset_code, verify_hr_reset_code, update_hr_verification_status , get_email_by_code_hr
from app.utils.jwt_utils import create_access_token, create_refresh_token, store_refresh_token
from app.utils.email_utils import send_email
from app.utils.response_schemas import success_response, error_response
from app.core.dependencies import verify_password


async def register_hr_user_logic(request, db: AsyncSession):
    if request.password != request.confirm_password:
        return error_response(code=400, error_message="Passwords do not match")

    existing_hr = await get_hr_by_email(request.business_email, db)
    if existing_hr:
        return error_response(code=400, error_message="Email already registered")

    await create_hr_user(request, db)

    code = str(random.randint(100000, 999999))
    await save_hr_reset_code(request.business_email, code, db)

    send_email(request.business_email, "Verify your HR account", f"Your code is: {code}")
    return success_response(code=201, data={"message": "Account created. Please verify it."})


async def verify_hr_user_logic(code: str, db: AsyncSession):
    email = await get_email_by_code_hr(code, db)
    if not email:
        return error_response(code=400, error_message="Invalid or expired verification code")

    is_valid = await verify_hr_reset_code(email, code, db)
    if not is_valid:
        return error_response(code=400, error_message="Invalid or expired verification code")

    await update_hr_verification_status(email, db)
    return success_response(code=200, data={"message": "HR account verified successfully."})


async def login_hr_user_logic(request, response, db: AsyncSession):
    hr_user = await get_hr_by_email(request.business_email, db)
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


async def resend_hr_verification_code_logic(email: str, db: AsyncSession):
    hr = await get_hr_by_email(email, db)
    if not hr:
        return error_response(code=404, error_message="HR user not found")

    if hr.is_verified:
        return error_response(code=400, error_message="Account already verified")

    new_code = str(random.randint(100000, 999999))
    await save_hr_reset_code(email, new_code, db)

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            send_email,
            hr.business_email,
            "Resend Verification Code",
            f"Your new verification code is: {new_code}"
        )
    except Exception as e:
        return error_response(code=500, error_message=f"Failed to send email: {str(e)}")

    return success_response(code=200, data={"message": "Verification code resent successfully"})
