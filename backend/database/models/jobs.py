# backend/database/models/jobs.py
import uuid
from sqlalchemy import Column, String, Integer, DateTime, func, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database.models.base import Base

class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = {'schema': 'tasks'}
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = Column(String(32), unique=True, index=True, nullable=True)  # ULID or UUIDv7
    user_id = Column(Integer, nullable=False, index=True)
    job_type = Column(String(32), nullable=False, index=True)  # 'render','video','text','email'
    status = Column(String(20), nullable=False, default="queued", index=True)  # queued, processing, done, failed
    attempts = Column(Integer, default=0)
    result_gridfs_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # relationship to detail
    render_detail = relationship("RenderJobDetail", back_populates="job", uselist=False, cascade="all, delete-orphan")


