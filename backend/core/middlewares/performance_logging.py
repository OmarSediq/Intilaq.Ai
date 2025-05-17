from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import time
from backend.core.logger import logger  

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = round(time.time() - start_time, 3)

        user = getattr(request.state, "user", None)
        user_id = user["user_id"] if user else "Anonymous"

        logger.info(
            f"[User: {user_id}] {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration}s"
        )
        return response
