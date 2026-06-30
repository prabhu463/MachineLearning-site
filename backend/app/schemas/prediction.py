from datetime import datetime

from pydantic import BaseModel

from backend.app.schemas.metric import MetricBase


class PredictionRequest(MetricBase):
    pass


class PredictionResponse(BaseModel):
    predicted_label: str
    risk_score: float
    confidence: float
    root_cause: str
    recommendation: str
    incident_created: bool
    incident_id: int | None = None
    created_at: datetime
