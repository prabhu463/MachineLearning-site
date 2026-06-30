from pydantic import BaseModel

from backend.app.schemas.incident import IncidentRead
from backend.app.schemas.metric import MetricRead


class DashboardSummary(BaseModel):
    total_metrics: int
    total_incidents: int
    open_incidents: int
    critical_incidents: int
    average_risk_score: float
    latest_metric: MetricRead | None
    latest_incident: IncidentRead | None
