from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.utils.jwt_utils import decode_access_token
import logging
from datetime import datetime, timezone

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("access_token")
        user = None

        if token:
            try:
                payload = decode_access_token(token)

                exp = payload.get("exp")
                if exp:
                    exp_time = datetime.fromtimestamp(exp, tz=timezone.utc)
                    now = datetime.now(timezone.utc)
                    if exp_time < now:
                        raise Exception("Token expired")

                user = {
                    "user_id": int(payload["user_id"]),
                    "role": payload.get("role", "regular_user")
                }
                request.state.user = user
                logging.info(f"[User {user['user_id']}] {request.method} {request.url.path}")
            except Exception as e:
                logging.warning(f"[Invalid Token] {request.url.path}: {e}")
        else:
            logging.info(f"[Anonymous] {request.method} {request.url.path}")

        return await call_next(request)
