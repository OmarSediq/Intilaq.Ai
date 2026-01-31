from dependency_injector.wiring import inject
from backend.domain_services.token_services.token_service import TokenService

@inject
def get_token_service(
) -> TokenService:
    return TokenService()
