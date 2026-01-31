from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from backend.domain_services.token_services.token_service import TokenService
import logging

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token_service = TokenService() 

        token = request.cookies.get("access_token")

        if token:
            try:
                payload = token_service.decode_access_token(token)

                user = {
                    "user_id": int(payload["user_id"]),
                    "role": payload.get("role", "regular_user")
                }

              
                request.state.user = user

                logging.info(f"[User {user['user_id']}] {request.method} {request.url.path}")

            except HTTPException as e:
                logging.warning(f"[Invalid Token] {request.url.path}: {e.detail}")
            except Exception as e:
                logging.error(f"[Token Error] {request.url.path}: {str(e)}")
        else:
            logging.info(f"[Anonymous] {request.method} {request.url.path}")

        return await call_next(request)
