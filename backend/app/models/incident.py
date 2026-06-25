from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.session import Base


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    metric_id: Mapped[int] = mapped_column(ForeignKey("metrics.id"), index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_label: Mapped[str] = mapped_column(String(32), nullable=False)
    root_cause: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
