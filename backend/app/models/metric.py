from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.session import Base


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service_name: Mapped[str] = mapped_column(String(120), index=True)
    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False)
    memory_usage: Mapped[float] = mapped_column(Float, nullable=False)
    disk_usage: Mapped[float] = mapped_column(Float, nullable=False)
    network_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
