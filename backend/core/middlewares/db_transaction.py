
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

class DBTransactionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            db: AsyncSession = getattr(request.state, "db", None)
            if db:
                await db.rollback()
            raise e
        

        