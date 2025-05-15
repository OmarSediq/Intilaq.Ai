from app.core.providers.data_access_providers.user_repository_provider import get_user_repository
from app.core.providers.domain_providers.token_provider import get_token_service
from app.data_access.postgres.user_repository import UserRepository
from app.domain_services.token_services.token_service import TokenService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.providers.infra_providers import get_db
from app.domain_services.auth_services.auth_service import AuthService
from app.domain_services.auth_services.account_service import AccountService
from app.domain_services.auth_services.password_service import PasswordRecoveryService

# ========== Auth ==========
def get_auth_service(
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
    token_service: TokenService = Depends(get_token_service)
) -> AuthService:
    return AuthService(db, user_repo, token_service)

def get_account_service(
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AccountService:
    return AccountService(db, user_repo)

def get_password_service(
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository)
) -> PasswordRecoveryService:
    return PasswordRecoveryService(db, user_repo)
