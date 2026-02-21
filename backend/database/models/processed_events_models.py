from sqlalchemy import Column, DateTime, PrimaryKeyConstraint, String, func
from backend.database.models.base import Base
class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    __table_args__ = (
        PrimaryKeyConstraint(
            "idempotency_key",
            "consumer_name",
            name="pk_processed_events",
        ),
        {"schema": "outbox"},
    )

    idempotency_key = Column(String, nullable=False)
    consumer_name = Column(String, nullable=False)

    processed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
