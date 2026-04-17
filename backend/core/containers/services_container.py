from dependency_injector import containers  , providers
from backend.domain_services.cv_services.cv_snapshot_builder_service import CVSnapshotBuilder
from backend.domain_services.cv_services.cv_download_service import CVDownloadService
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.domain_services.token_services.token_service import TokenService
from backend.domain_services.token_services.refresh_token_service import RefreshTokenService



class ServicesContainer (containers.DeclarativeContainer):
    infra = providers.DependenciesContainer() 
    repos = providers.DependenciesContainer()  

    token_service = providers.Singleton(
        TokenService
        
    )
    refresh_token_service = providers.Singleton(
        RefreshTokenService,
        redis_client=infra.redis_client
    )

    validator_service = providers.Factory(
        InterviewValidatorService,
        repo_interview=repos.interview_repository_factory,
        repo_session=repos.session_redis_repository
    )


    cv_snapshot_builder_service = providers.Factory(
        CVSnapshotBuilder
    )

    cv_download_service = providers.Factory(CVDownloadService)



    
