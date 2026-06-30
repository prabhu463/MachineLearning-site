from datetime import datetime

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    metric_id: int
    severity: str
    risk_score: float = Field(ge=0, le=1)
    predicted_label: str
    root_cause: str
    recommendation: str
    notes: str = ""


class IncidentUpdate(BaseModel):
    status: str
    notes: str = ""


class IncidentRead(BaseModel):
    """Full incident representation returned from the API.

    Declared as a standalone model (not inheriting IncidentCreate) so that
    all fields are explicit and ORM serialization is unambiguous.
    """

    id: int
    metric_id: int
    severity: str
    risk_score: float
    predicted_label: str
    root_cause: str
    recommendation: str
    status: str
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}

