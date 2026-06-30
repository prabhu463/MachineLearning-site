from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.session import Base


class Alert(Base):
    """Threshold-based alert rule.

    When the alert evaluator (Phase 3 worker) detects that a metric field
    crosses ``threshold_value``, it creates an incident and can trigger a
    notification.

    Operators
    ---------
    gt  — greater than
    lt  — less than
    gte — greater than or equal
    lte — less than or equal

    Channels
    --------
    email | slack | webhook | none
    """

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    # The metric field this rule watches (e.g. "cpu_usage", "error_rate")
    metric_field: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    # Comparison operator: gt | lt | gte | lte
    operator: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    # Severity to assign when the alert fires
    severity: Mapped[str] = mapped_column(String(20), default="warning", nullable=False)
    # Notification channel: email | slack | webhook | none
    channel: Mapped[str] = mapped_column(String(30), default="none", nullable=False)
    channel_target: Mapped[str] = mapped_column(String(255), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_alerts_active_field", "is_active", "metric_field"),
    )
