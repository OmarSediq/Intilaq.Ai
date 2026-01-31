from typing import Optional
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound

from backend.database.models.jobs import Job  
from backend.database.models.render_jobs_detail import RenderJobDetail


class JobRepository:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_by_idempotency(self, key: str) -> Optional[Job]:
        async with self._session_factory() as session:
            q = await session.execute(select(Job).where(Job.idempotency_key == key))
            row = q.scalars().first()
            return row

    async def create_pending_job_with_render_detail(self, job_id: str, idempotency_key: str, user_id: int, job_type: str):
        """
        Create job (status pending) AND create associated render_detail (html_gridfs_id NULL)
        within a single transaction.
        """
        async with self._session_factory() as session:
            async with session.begin():
                job = Job(
                    id=job_id,
                    idempotency_key=idempotency_key,
                    user_id=user_id,
                    job_type=job_type,
                    status="pending",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(job)
                # create render detail row with null html_gridfs_id
                detail = RenderJobDetail(
                    job_id=job_id,
                    html_gridfs_id=None,
                    filename=None,
                    renderer_options=None,
                    page_count=None
                )
                session.add(detail)
            # commit happens at context exit

    async def update_render_detail(self, job_id: str, html_gridfs_id: str, filename: str, renderer_options: dict):
        async with self._session_factory() as session:
            async with session.begin():
                # Option A: query the object and update fields
                detail = await session.get(RenderJobDetail, job_id)
                if not detail:
                    # optional: raise or create
                    raise NoResultFound(f"Render detail for job {job_id} not found")
                detail.html_gridfs_id = html_gridfs_id
                detail.filename = filename
                detail.renderer_options = renderer_options
                # session will flush on commit

    async def mark_job_queued(self, job_id: str):
        async with self._session_factory() as session:
            async with session.begin():
                job = await session.get(Job, job_id)
                if not job:
                    raise NoResultFound(f"Job {job_id} not found")
                job.status = "queued"
                job.updated_at = datetime.utcnow()

    async def mark_job_failed(self, job_id: str, error: str):
        async with self._session_factory() as session:
            async with session.begin():
                job = await session.get(Job, job_id)
                if not job:
                    raise NoResultFound(f"Job {job_id} not found")
                job.status = "failed"
                job.last_error = error
                job.updated_at = datetime.utcnow()

    async def increment_attempts_and_mark_processing(self, job_id: str):
        async with self._session_factory() as session:
            async with session.begin():
                job = await session.get(Job, job_id)
                if not job:
                    raise NoResultFound(f"Job {job_id} not found")
                job.attempts = (job.attempts or 0) + 1
                job.status = "processing"
                job.updated_at = datetime.utcnow()

    # utility: for heavy queries, you may still drop to raw SQL within repository
    async def get_jobs_summary(self):
        async with self._session_factory() as session:
            # Example: use SQLAlchemy Core or raw SQL for aggregation if needed
            result = await session.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
            return result.all()
