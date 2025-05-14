from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db

from app.services.auth_services.auth_service import AuthService
from app.services.auth_services.account_service import AccountService
from app.services.auth_services.password_service import PasswordRecoveryService

# ========== Auth ==========
def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_account_service(db: AsyncSession = Depends(get_db)) -> AccountService:
    return AccountService(db)

def get_password_service(db: AsyncSession = Depends(get_db)) -> PasswordRecoveryService:
    return PasswordRecoveryService(db)
