from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies.session.postgres import provide_request_postgres_session
from backend.domain_services.auth_services.auth_service import AuthService
from backend.domain_services.auth_services.account_service import AccountService
from backend.domain_services.auth_services.password_service import PasswordRecoveryService
from backend.data_access.postgres.user_repository import UserRepository
from dependency_injector.wiring import inject , Provide
from backend.core.containers.application_container import ApplicationContainer

@inject
async def get_auth_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    ## Lazy manual construction 
    user_repo_factory: Callable[[AsyncSession], UserRepository] = Depends(
    Provide[ApplicationContainer.repos.user_repository_factory.provider]

    ),
    token_service = Depends(
        Provide[ApplicationContainer.service.token_service]),
    refresh_token_service  = Depends(Provide[ApplicationContainer.service.refresh_token_service])
    ,
) -> AuthService:
    user_repo = user_repo_factory(db)
    return AuthService(db, user_repo, token_service , refresh_token_service)


@inject
async def get_account_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    user_repo_factory = Depends(
        Provide[ApplicationContainer.repos.user_repository_factory.provider]
    ),
) -> AccountService:
    user_repo = user_repo_factory(db)
    return AccountService(db, user_repo)


@inject
async def get_password_service(
    db: AsyncSession = Depends(provide_request_postgres_session),
    user_repo_factory = Depends(
        Provide[ApplicationContainer.repos.user_repository_factory.provider]
    ),
) -> PasswordRecoveryService:
    user_repo = user_repo_factory(db)
    return PasswordRecoveryService(db, user_repo)