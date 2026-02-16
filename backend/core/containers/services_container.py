from dependency_injector import containers  , providers
from backend.domain_services.interview_services.validator_service import InterviewValidatorService
from backend.domain_services.token_services.token_service import TokenService
from backend.domain_services.token_services.refresh_token_service import RefreshTokenService
from backend.core.config import env 
from backend.domain_services.doc_services.resume_html_renderer import ResumeHTMLRenderer


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
        repo_interview=repos.interview_repository,
        repo_session=repos.session_redis_repository
    )

    resume_html_renderer = providers.Factory(
        ResumeHTMLRenderer,
        env=env
    )

    



    
