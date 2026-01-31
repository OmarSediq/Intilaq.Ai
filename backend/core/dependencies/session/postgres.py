from typing import AsyncGenerator
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

async def provide_request_postgres_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.session_factory() as session:
        request.state.db = session
        yield session
