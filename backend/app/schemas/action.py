from datetime import datetime

from pydantic import BaseModel


class ActionCreate(BaseModel):
    incident_id: int
    action_name: str
    executed_by: str = "automation-bot"
    details: str = ""


class ActionRead(ActionCreate):
    id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
