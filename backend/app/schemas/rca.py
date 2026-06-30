from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RCAResponse(BaseModel):
    """Root Cause Analysis result for a specific incident."""

    incident_id: int
    root_cause: str
    recommendation: str
    rationale: str
    confidence: float | None = None
    analyzed_at: datetime
