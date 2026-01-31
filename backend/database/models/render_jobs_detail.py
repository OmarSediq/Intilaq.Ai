# backend/database/models/render_jobs_detail.py
from sqlalchemy import Column, String, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database.models.base import Base

class RenderJobDetail(Base):
    __tablename__ = "render_jobs_detail"
    __table_args__ = {'schema': 'tasks'}
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    html_gridfs_id = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    renderer_options = Column(JSON, nullable=True)  # width, scale, margins...
    page_count = Column(Integer, nullable=True)

    job = relationship("Job", back_populates="render_detail")
