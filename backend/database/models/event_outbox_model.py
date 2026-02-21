# backend/database/models/jobs.py
import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, func, Enum , Index
from backend.database.models.base import Base
from sqlalchemy.dialects.postgresql import UUID, JSONB

class OutboxStatus(str):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"
    
class EventOutbox(Base):
    __tablename__ = "events_outbox"

    __table_args__ = (
        Index("ix_outbox_scheduler", "status", "scheduled_at"),
        {"schema": "outbox"},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_name = Column(String, nullable=False)
    version = Column(Integer, nullable=False)

    payload = Column(JSONB, nullable=False)

    idempotency_key = Column(String, nullable=False, unique=True)

    status = Column(
        Enum(
            OutboxStatus.PENDING,
            OutboxStatus.DISPATCHED,
            OutboxStatus.FAILED,
            name="outbox_status_enum",
            schema="outbox",   # ✔️ متوافق الآن
        ),
        nullable=False,
        default=OutboxStatus.PENDING,
    )

    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    attempt_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    dispatched_at = Column(DateTime(timezone=True), nullable=True)
