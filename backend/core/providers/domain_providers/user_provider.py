from fastapi import Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from backend.core.containers.services_container import ServicesContainer
from backend.domain_services.token_services.token_service import TokenService

async def get_current_user(
    token_service: TokenService = Depends(Provide[ServicesContainer.token_service]),
    authorization: str = Depends(lambda req: req.headers.get("Authorization"))
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = await token_service.get_user_from_token(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
